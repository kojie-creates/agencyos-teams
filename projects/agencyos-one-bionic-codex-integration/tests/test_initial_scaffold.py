import warnings
from pathlib import Path

warnings.filterwarnings(
    "ignore",
    category=Warning,
    module=r"fastapi\.testclient",
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_initial_scaffold_files_exist():
    expected_paths = [
        ".dockerignore",
        "README.md",
        "Dockerfile",
        ".env.example",
        "requirements.txt",
        "src/api_gateway.py",
        "src/artifact_repository.py",
        "src/data_source_trust_module.py",
        "src/external_adapter.py",
        "src/forecasting_engine.py",
        "src/monitoring.py",
        "src/orchestrator.py",
        "src/policy_checker.py",
        "tests/test_initial_scaffold.py",
    ]

    for relative_path in expected_paths:
        assert (PROJECT_ROOT / relative_path).is_file()


def test_initial_scaffold_directories_exist():
    expected_paths = [
        "src",
        "tests",
    ]

    for relative_path in expected_paths:
        assert (PROJECT_ROOT / relative_path).is_dir()


def test_policy_checker_stub_passes():
    import sys

    sys.path.insert(0, str(PROJECT_ROOT / "src"))
    from policy_checker import check_policy

    result = check_policy({"goal": "validate scaffold"})

    assert result["status"] == "PASS"


def test_policy_engine_passes_clean_context():
    import sys

    sys.path.insert(0, str(PROJECT_ROOT / "src"))
    from policy_checker import PolicyEngine

    result = PolicyEngine().check_compliance(
        "Draft a local internal runbook for the onboarding workflow."
    )

    assert result["status"] == "PASS"
    assert result["reason"] == "NO_POLICY_VIOLATION"
    assert result["required_action"] == "NONE"


def test_policy_engine_fails_when_pii_detected():
    import sys

    sys.path.insert(0, str(PROJECT_ROOT / "src"))
    from policy_checker import PolicyEngine

    result = PolicyEngine().check_compliance(
        "Contact user@example.com before the workflow starts."
    )

    assert result == {
        "status": "FAIL",
        "reason": "PII_DETECTED",
        "required_action": "MASKING",
        "source": "CLI",
    }


def test_policy_engine_flags_high_risk_keyword():
    import sys

    sys.path.insert(0, str(PROJECT_ROOT / "src"))
    from policy_checker import PolicyEngine

    result = PolicyEngine().check_compliance(
        "Prepare the acquisition planning memo for review."
    )

    assert result == {
        "status": "FLAGGED",
        "reason": "HIGH_RISK_KEYWORD",
        "required_action": "HUMAN_REVIEW",
        "source": "CLI",
    }


def test_policy_engine_does_not_flag_absent_high_risk_keyword():
    import sys

    sys.path.insert(0, str(PROJECT_ROOT / "src"))
    from policy_checker import PolicyEngine

    result = PolicyEngine().check_compliance(
        "Prepare an internal product positioning note."
    )

    assert result["status"] == "PASS"
    assert result["reason"] == "NO_POLICY_VIOLATION"


def test_orchestrator_initializes_workflow():
    import sys

    sys.path.insert(0, str(PROJECT_ROOT / "src"))
    from orchestrator import IntegrationOrchestrator

    result = IntegrationOrchestrator().initialize_workflow("validate scaffold")

    assert result["status"] == "initialized"
    assert result["goal"] == "validate scaffold"


def test_policy_gate_halt():
    import sys

    sys.path.insert(0, str(PROJECT_ROOT / "src"))
    from orchestrator import IntegrationOrchestrator

    result = IntegrationOrchestrator().run_workflow(
        "Prepare acquisition plan for external send.",
        source_context="HANDOFF_PACKAGE",
    )

    assert result["status"] == "HALTED"
    assert result["message"].startswith("Workflow Halted by Policy Gate.")
    assert result["policy"]["reason"] == "HIGH_RISK_KEYWORD"
    assert result["required_action"] == "HUMAN_REVIEW"
    assert result["core_services_executed"] is False


def test_asset_transaction_logging(tmp_path):
    import hashlib
    import sys

    sys.path.insert(0, str(PROJECT_ROOT / "src"))
    from artifact_repository import ArtifactRepository
    from orchestrator import IntegrationOrchestrator

    asset_file = tmp_path / "asset.txt"
    asset_file.write_text("asset payload for transaction logging", encoding="utf-8")
    repository = ArtifactRepository(tmp_path / "transaction-store")

    result = IntegrationOrchestrator(
        artifact_repository=repository,
    ).process_asset(
        str(asset_file),
        transaction_metadata={"source": "unit-test"},
    )

    transaction_id = result["transaction_id"]
    stored = repository.get_transaction(transaction_id)

    assert result["status"] == "COMPLETED"
    assert transaction_id
    assert stored["transaction_id"] == transaction_id
    assert stored["source_file"] == str(asset_file)
    assert stored["status"] == "PROCESSED"
    assert stored["sha256"] == hashlib.sha256(asset_file.read_bytes()).hexdigest()


def test_artifact_repository_uses_simulated_database_write(tmp_path):
    import sys

    sys.path.insert(0, str(PROJECT_ROOT / "src"))
    from artifact_repository import ArtifactRepository

    class RecordingDatabase:
        def __init__(self):
            self.transactions = []

        def write_transaction(self, data):
            self.transactions.append(data)
            return {
                "status": "SIMULATED",
                "message": "Persistence simulated by placeholder database.",
            }

    db = RecordingDatabase()
    asset_file = tmp_path / "asset.txt"
    asset_file.write_text("asset payload for persistence hook", encoding="utf-8")
    repository = ArtifactRepository(tmp_path / "transaction-store", db=db)

    transaction_id = repository.log_asset_transaction(
        source_file=str(asset_file),
        status="PROCESSED",
        transaction_metadata={"source": "persistence-test"},
    )
    stored = repository.get_transaction(transaction_id)

    assert len(db.transactions) == 1
    assert db.transactions[0]["transaction_id"] == transaction_id
    assert stored["persistence"] == {
        "status": "SIMULATED",
        "message": "Persistence simulated by placeholder database.",
    }


def test_full_lifecycle_success(tmp_path):
    import sys

    sys.path.insert(0, str(PROJECT_ROOT / "src"))
    from artifact_repository import ArtifactRepository
    from orchestrator import IntegrationOrchestrator

    repository = ArtifactRepository(tmp_path / "transaction-store")
    orchestrator = IntegrationOrchestrator(
        artifact_repository=repository,
        asset_workspace=tmp_path / "assets",
    )

    result = orchestrator.execute_master_workflow(
        goal="Draft an internal onboarding charter.",
        source_context="CLI",
    )

    assert result["status"] == "COMPLETED"
    assert result["policy"]["status"] == "PASS"
    assert result["charter"]["status"] == "CHARTER_CREATED"
    assert result["asset"]["status"] == "COMPLETED"
    assert result["final_transaction_id"].startswith("txn-")
    assert result["service_call_order"] == [
        "policy_check",
        "charter",
        "asset_processor",
        "transaction_manifest",
    ]

    stored = repository.get_transaction(result["final_transaction_id"])

    assert stored["transaction_id"] == result["final_transaction_id"]
    assert stored["transaction_metadata"]["asset_transaction_id"] == result["asset"]["transaction_id"]
    assert stored["transaction_metadata"]["charter_id"] == result["charter"]["charter_id"]


def test_api_gateway_workflow_start_success():
    import sys

    sys.path.insert(0, str(PROJECT_ROOT / "src"))
    from api_gateway import ApiGateway

    def workflow_runner(goal, source_context):
        return {
            "status": "COMPLETED",
            "goal": goal,
            "source_context": source_context,
            "policy": {
                "status": "PASS",
                "reason": "NO_POLICY_VIOLATION",
                "required_action": "NONE",
                "source": source_context,
            },
            "final_transaction_id": "txn-test",
        }

    response = ApiGateway(workflow_runner=workflow_runner).handle_request(
        method="POST",
        path="/v1/workflow/start",
        json_body={
            "goal": "Draft an internal onboarding charter.",
            "source_context": "CLI",
        },
    )

    assert response["status_code"] == 200
    assert response["body"]["success"] is True
    assert response["body"]["status"] == "COMPLETED"
    assert response["body"]["policy"]["status"] == "PASS"
    assert response["body"]["final_transaction_id"] == "txn-test"


def test_api_gateway_policy_failure_returns_403_without_workflow_execution():
    import sys

    sys.path.insert(0, str(PROJECT_ROOT / "src"))
    from api_gateway import ApiGateway

    calls = []

    def workflow_runner(goal, source_context):
        calls.append((goal, source_context))
        return {"status": "COMPLETED"}

    response = ApiGateway(workflow_runner=workflow_runner).handle_request(
        method="POST",
        path="/v1/workflow/start",
        json_body={
            "goal": "Prepare acquisition plan for external send.",
            "source_context": "HANDOFF_PACKAGE",
        },
    )

    assert response["status_code"] == 403
    assert response["body"]["success"] is False
    assert response["body"]["status"] == "HALTED"
    assert response["body"]["policy"]["reason"] == "HIGH_RISK_KEYWORD"
    assert response["body"]["required_action"] == "HUMAN_REVIEW"
    assert calls == []


def test_http_service_accepts_valid_api_key_for_workflow_start():
    import sys

    sys.path.insert(0, str(PROJECT_ROOT / "src"))
    from api_gateway import ApiGateway
    from api_gateway import create_app

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        from fastapi.testclient import TestClient

    def workflow_runner(goal, source_context):
        return {
            "status": "COMPLETED",
            "goal": goal,
            "source_context": source_context,
            "final_transaction_id": "txn-http-test",
        }

    app = create_app(
        api_gateway=ApiGateway(workflow_runner=workflow_runner),
        api_key="test-key",
    )
    response = TestClient(app).post(
        "/v1/workflow/start",
        headers={"X-API-KEY": "test-key"},
        json={
            "goal": "Draft an internal onboarding charter.",
            "source_context": "HTTP_TEST",
        },
    )

    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["status"] == "COMPLETED"
    assert response.json()["final_transaction_id"] == "txn-http-test"


def test_http_service_rejects_missing_or_invalid_api_key_before_policy():
    import sys

    sys.path.insert(0, str(PROJECT_ROOT / "src"))
    from api_gateway import ApiGateway
    from api_gateway import create_app

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        from fastapi.testclient import TestClient

    class SpyPolicyEngine:
        def __init__(self):
            self.calls = []

        def check_compliance(self, input_context, source=None):
            self.calls.append((input_context, source))
            return {
                "status": "PASS",
                "reason": "NO_POLICY_VIOLATION",
                "required_action": "NONE",
                "source": source or "CLI",
            }

        def is_blocking(self, policy_result):
            return False

    policy_engine = SpyPolicyEngine()
    client = TestClient(
        create_app(
            api_gateway=ApiGateway(policy_engine=policy_engine),
            api_key="test-key",
        )
    )

    missing = client.post(
        "/v1/workflow/start",
        json={"goal": "Prepare acquisition plan for external send."},
    )
    invalid = client.post(
        "/v1/workflow/start",
        headers={"X-API-KEY": "wrong-key"},
        json={"goal": "Prepare acquisition plan for external send."},
    )

    assert missing.status_code == 401
    assert missing.json() == {
        "success": False,
        "error": "UNAUTHORIZED",
    }
    assert invalid.status_code == 401
    assert invalid.json() == {
        "success": False,
        "error": "UNAUTHORIZED",
    }
    assert policy_engine.calls == []


def test_http_service_returns_policy_failure_after_valid_api_key():
    import sys

    sys.path.insert(0, str(PROJECT_ROOT / "src"))
    from api_gateway import create_app

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        from fastapi.testclient import TestClient

    client = TestClient(create_app(api_key="test-key"))
    response = client.post(
        "/v1/workflow/start",
        headers={"X-API-KEY": "test-key"},
        json={
            "goal": "Prepare acquisition plan for external send.",
            "source_context": "HTTP_TEST",
        },
    )

    assert response.status_code == 403
    assert response.json()["success"] is False
    assert response.json()["status"] == "HALTED"
    assert response.json()["policy"]["reason"] == "HIGH_RISK_KEYWORD"


def test_api_gateway_policy_check_endpoint():
    import sys

    sys.path.insert(0, str(PROJECT_ROOT / "src"))
    from api_gateway import ApiGateway

    response = ApiGateway().handle_request(
        method="GET",
        path="/v1/policy/check",
        query={"input": "Contact user@example.com for onboarding."},
    )

    assert response["status_code"] == 200
    assert response["body"] == {
        "success": True,
        "policy": {
            "status": "FAIL",
            "reason": "PII_DETECTED",
            "required_action": "MASKING",
            "source": "CLI",
        },
    }


def test_api_gateway_transaction_retrieval_endpoint(tmp_path):
    import sys

    sys.path.insert(0, str(PROJECT_ROOT / "src"))
    from api_gateway import ApiGateway
    from artifact_repository import ArtifactRepository

    asset_file = tmp_path / "asset.txt"
    asset_file.write_text("asset payload for api retrieval", encoding="utf-8")
    repository = ArtifactRepository(tmp_path / "transaction-store")
    transaction_id = repository.log_asset_transaction(
        source_file=str(asset_file),
        status="PROCESSED",
        transaction_metadata={"source": "api-test"},
    )

    response = ApiGateway(artifact_repository=repository).handle_request(
        method="GET",
        path=f"/v1/transactions/{transaction_id}",
    )

    assert response["status_code"] == 200
    assert response["body"]["success"] is True
    assert response["body"]["transaction"]["transaction_id"] == transaction_id
    assert response["body"]["transaction"]["status"] == "PROCESSED"


def test_monitoring_service_successful_diagnostic_report():
    import sys

    sys.path.insert(0, str(PROJECT_ROOT / "src"))
    from monitoring import MonitoringService

    result = MonitoringService().run_diagnostics(
        input_context="Run internal health diagnostics.",
        source_context="CLI",
    )

    assert result["status"] == "PASS"
    assert result["source_context"] == "CLI"
    assert result["summary"] == "SIMULATED_DIAGNOSTICS_COMPLETE"
    assert result["checks"] == {
        "policy_engine_available": "PASS",
        "artifact_repository_available": "PASS",
        "api_gateway_contract_available": "PASS",
    }


def test_diagnostics_policy_halt_before_monitoring():
    import sys

    sys.path.insert(0, str(PROJECT_ROOT / "src"))
    from orchestrator import IntegrationOrchestrator

    result = IntegrationOrchestrator().run_diagnostics(
        input_context="Run acquisition diagnostics.",
        source_context="CLI",
    )

    assert result["status"] == "HALTED"
    assert result["policy"]["reason"] == "HIGH_RISK_KEYWORD"
    assert result["service_call_order"] == ["policy_check"]
    assert result["diagnostics_executed"] is False


def test_diagnostics_transaction_manifest_creation(tmp_path):
    import sys

    sys.path.insert(0, str(PROJECT_ROOT / "src"))
    from artifact_repository import ArtifactRepository
    from orchestrator import IntegrationOrchestrator

    repository = ArtifactRepository(tmp_path / "transaction-store")
    orchestrator = IntegrationOrchestrator(
        artifact_repository=repository,
        asset_workspace=tmp_path / "assets",
    )

    result = orchestrator.run_diagnostics(
        input_context="Run internal health diagnostics.",
        source_context="CLI",
    )

    stored = repository.get_transaction(result["transaction_id"])

    assert result["status"] == "COMPLETED"
    assert result["policy"]["status"] == "PASS"
    assert result["diagnostics"]["status"] == "PASS"
    assert result["service_call_order"] == [
        "policy_check",
        "monitoring_service",
        "transaction_manifest",
    ]
    assert stored["transaction_id"] == result["transaction_id"]
    assert stored["status"] == "DIAGNOSTICS_COMPLETED"
    assert stored["transaction_metadata"]["workflow_step"] == "diagnostics"


def test_api_gateway_diagnose_endpoint_response_shape(tmp_path):
    import sys

    sys.path.insert(0, str(PROJECT_ROOT / "src"))
    from api_gateway import ApiGateway
    from artifact_repository import ArtifactRepository
    from orchestrator import IntegrationOrchestrator

    repository = ArtifactRepository(tmp_path / "transaction-store")
    orchestrator = IntegrationOrchestrator(
        artifact_repository=repository,
        asset_workspace=tmp_path / "assets",
    )
    gateway = ApiGateway(
        diagnostic_runner=orchestrator.run_diagnostics,
        artifact_repository=repository,
    )

    response = gateway.handle_request(
        method="GET",
        path="/v1/diagnose",
        query={
            "input": "Run internal health diagnostics.",
            "source_context": "CLI",
        },
    )

    assert response["status_code"] == 200
    assert response["body"]["success"] is True
    assert response["body"]["status"] == "COMPLETED"
    assert response["body"]["diagnostics"]["checks"]["policy_engine_available"] == "PASS"
    assert response["body"]["transaction_id"].startswith("txn-")


def test_external_adapter_successful_api_call_simulation(tmp_path):
    import sys

    sys.path.insert(0, str(PROJECT_ROOT / "src"))
    from api_gateway import ApiGateway
    from artifact_repository import ArtifactRepository

    spec_file = tmp_path / "crm-openapi.yaml"
    spec_file.write_text("openapi: 3.0.0\ninfo:\n  title: CRM\n", encoding="utf-8")
    repository = ArtifactRepository(tmp_path / "transaction-store")

    response = ApiGateway(
        artifact_repository=repository,
        external_workspace=tmp_path / "external-attempts",
    ).handle_request(
        method="POST",
        path="/v1/external/crm/accounts",
        json_body={
            "input_context": "Sync internal account summary.",
            "source_context": "CLI",
            "openapi_spec": str(spec_file),
            "credentials": {
                "token": "scoped-token",
                "scopes": ["crm:accounts"],
            },
            "payload": {"account_id": "acct-001"},
        },
    )

    stored = repository.get_transaction(response["body"]["transaction_id"])

    assert response["status_code"] == 200
    assert response["body"]["success"] is True
    assert response["body"]["status"] == "COMPLETED"
    assert response["body"]["external_call"]["status"] == "PASS"
    assert response["body"]["external_call"]["service"] == "crm"
    assert response["body"]["external_call"]["endpoint"] == "accounts"
    assert stored["status"] == "EXTERNAL_CALL_COMPLETED"
    assert stored["transaction_metadata"]["result"] == "success"
    assert stored["transaction_metadata"]["error_code"] is None


def test_external_adapter_policy_halt_logs_attempt(tmp_path):
    import sys

    sys.path.insert(0, str(PROJECT_ROOT / "src"))
    from api_gateway import ApiGateway
    from artifact_repository import ArtifactRepository

    spec_file = tmp_path / "crm-openapi.yaml"
    spec_file.write_text("openapi: 3.0.0\n", encoding="utf-8")
    repository = ArtifactRepository(tmp_path / "transaction-store")

    response = ApiGateway(
        artifact_repository=repository,
        external_workspace=tmp_path / "external-attempts",
    ).handle_request(
        method="POST",
        path="/v1/external/crm/accounts",
        json_body={
            "input_context": "Sync internal account summary.",
            "source_context": "CLI",
            "openapi_spec": str(spec_file),
            "credentials": {
                "token": "scoped-token",
                "scopes": ["crm:contacts"],
            },
            "payload": {"account_id": "acct-001"},
        },
    )

    stored = repository.get_transaction(response["body"]["transaction_id"])

    assert response["status_code"] == 403
    assert response["body"]["success"] is False
    assert response["body"]["status"] == "HALTED"
    assert response["body"]["policy"]["reason"] == "INVALID_CREDENTIAL_SCOPE"
    assert stored["status"] == "EXTERNAL_CALL_POLICY_HALTED"
    assert stored["transaction_metadata"]["result"] == "policy_halt"
    assert stored["transaction_metadata"]["error_code"] == "INVALID_CREDENTIAL_SCOPE"


def test_external_adapter_external_failure_logs_attempt(tmp_path):
    import sys

    sys.path.insert(0, str(PROJECT_ROOT / "src"))
    from api_gateway import ApiGateway
    from artifact_repository import ArtifactRepository

    spec_file = tmp_path / "crm-openapi.yaml"
    spec_file.write_text("openapi: 3.0.0\n", encoding="utf-8")
    repository = ArtifactRepository(tmp_path / "transaction-store")

    response = ApiGateway(
        artifact_repository=repository,
        external_workspace=tmp_path / "external-attempts",
    ).handle_request(
        method="POST",
        path="/v1/external/crm/fail-endpoint",
        json_body={
            "input_context": "Sync internal account summary.",
            "source_context": "CLI",
            "openapi_spec": str(spec_file),
            "credentials": {
                "token": "scoped-token",
                "scopes": ["crm:fail-endpoint"],
            },
            "payload": {"simulate_error": "UPSTREAM_TIMEOUT"},
        },
    )

    stored = repository.get_transaction(response["body"]["transaction_id"])

    assert response["status_code"] == 502
    assert response["body"]["success"] is False
    assert response["body"]["status"] == "FAILED"
    assert response["body"]["error_code"] == "UPSTREAM_TIMEOUT"
    assert stored["status"] == "EXTERNAL_CALL_FAILED"
    assert stored["transaction_metadata"]["result"] == "failure"
    assert stored["transaction_metadata"]["error_code"] == "UPSTREAM_TIMEOUT"


def test_data_source_trust_trusted_source_passes():
    import sys

    sys.path.insert(0, str(PROJECT_ROOT / "src"))
    from data_source_trust_module import DataSourceTrustService

    result = DataSourceTrustService().validate_source(
        {
            "source_name": "approved-audit-log",
            "owner_approved": True,
            "consent_status": "APPROVED",
            "reliability_rating": 0.92,
            "data_age_days": 5,
        }
    )

    assert result["status"] == "PASS"
    assert result["reason"] == "DATA_SOURCE_TRUSTED"
    assert result["required_action"] == "NONE"


def test_data_source_trust_missing_consent_halts(tmp_path):
    import sys

    sys.path.insert(0, str(PROJECT_ROOT / "src"))
    from api_gateway import ApiGateway
    from artifact_repository import ArtifactRepository

    repository = ArtifactRepository(tmp_path / "transaction-store")

    response = ApiGateway(
        artifact_repository=repository,
        data_source_workspace=tmp_path / "data-source-attempts",
    ).handle_request(
        method="POST",
        path="/v1/data-source/validate",
        json_body={
            "input_context": "Validate audit source for forecasting.",
            "source_context": "CLI",
            "source": {
                "source_name": "unapproved-audit-log",
                "owner_approved": True,
                "consent_status": "MISSING",
                "reliability_rating": 0.9,
                "data_age_days": 3,
            },
        },
    )

    stored = repository.get_transaction(response["body"]["transaction_id"])

    assert response["status_code"] == 403
    assert response["body"]["success"] is False
    assert response["body"]["status"] == "HALTED"
    assert response["body"]["trust_result"]["reason"] == "CONSENT_NOT_APPROVED"
    assert stored["status"] == "DATA_SOURCE_VALIDATION_HALTED"
    assert stored["transaction_metadata"]["result"] == "halted"
    assert stored["transaction_metadata"]["reason"] == "CONSENT_NOT_APPROVED"


def test_data_source_trust_stale_source_flags(tmp_path):
    import sys

    sys.path.insert(0, str(PROJECT_ROOT / "src"))
    from api_gateway import ApiGateway
    from artifact_repository import ArtifactRepository

    repository = ArtifactRepository(tmp_path / "transaction-store")

    response = ApiGateway(
        artifact_repository=repository,
        data_source_workspace=tmp_path / "data-source-attempts",
    ).handle_request(
        method="POST",
        path="/v1/data-source/validate",
        json_body={
            "input_context": "Validate audit source for forecasting.",
            "source_context": "CLI",
            "source": {
                "source_name": "old-audit-log",
                "owner_approved": True,
                "consent_status": "APPROVED",
                "reliability_rating": 0.88,
                "data_age_days": 45,
            },
        },
    )

    stored = repository.get_transaction(response["body"]["transaction_id"])

    assert response["status_code"] == 202
    assert response["body"]["success"] is False
    assert response["body"]["status"] == "FLAGGED"
    assert response["body"]["trust_result"]["reason"] == "DATA_SOURCE_STALE"
    assert stored["status"] == "DATA_SOURCE_VALIDATION_FLAGGED"
    assert stored["transaction_metadata"]["result"] == "flagged"


def test_data_source_trust_low_reliability_flags(tmp_path):
    import sys

    sys.path.insert(0, str(PROJECT_ROOT / "src"))
    from data_source_trust_module import DataSourceTrustService

    result = DataSourceTrustService().validate_source(
        {
            "source_name": "thin-audit-log",
            "owner_approved": True,
            "consent_status": "APPROVED",
            "reliability_rating": 0.62,
            "data_age_days": 7,
        }
    )

    assert result["status"] == "FLAGGED"
    assert result["reason"] == "LOW_RELIABILITY_SOURCE"
    assert result["required_action"] == "HUMAN_REVIEW"


def test_data_source_trust_successful_logging_attempt(tmp_path):
    import sys

    sys.path.insert(0, str(PROJECT_ROOT / "src"))
    from api_gateway import ApiGateway
    from artifact_repository import ArtifactRepository

    repository = ArtifactRepository(tmp_path / "transaction-store")

    response = ApiGateway(
        artifact_repository=repository,
        data_source_workspace=tmp_path / "data-source-attempts",
    ).handle_request(
        method="POST",
        path="/v1/data-source/validate",
        json_body={
            "input_context": "Validate audit source for forecasting.",
            "source_context": "CLI",
            "source": {
                "source_name": "approved-audit-log",
                "owner_approved": True,
                "consent_status": "APPROVED",
                "reliability_rating": 0.95,
                "data_age_days": 2,
            },
        },
    )

    stored = repository.get_transaction(response["body"]["transaction_id"])

    assert response["status_code"] == 200
    assert response["body"]["success"] is True
    assert response["body"]["status"] == "COMPLETED"
    assert response["body"]["trust_result"]["status"] == "PASS"
    assert stored["status"] == "DATA_SOURCE_VALIDATION_COMPLETED"
    assert stored["transaction_metadata"]["workflow_step"] == "data_source_trust"
    assert stored["transaction_metadata"]["result"] == "trusted"


def test_forecasting_engine_simulates_prediction_from_trusted_context():
    import sys

    sys.path.insert(0, str(PROJECT_ROOT / "src"))
    from forecasting_engine import ForecastingEngine

    result = ForecastingEngine().run_prediction(
        source_context={
            "status": "PASS",
            "reason": "DATA_SOURCE_TRUSTED",
            "source_name": "approved-audit-log",
        },
        input_payload={
            "baseline_risk": 0.4,
            "volatility": 0.2,
            "exposure": 0.3,
        },
    )

    assert result["status"] == "PASS"
    assert result["forecasted_risk_score"] == 0.6
    assert result["predicted_outcome"] == "MODERATE_RISK"
    assert result["confidence_interval"] == {
        "lower_bound": 0.5,
        "upper_bound": 0.7,
    }
    assert result["human_review_required"] is True
    assert result["governance_metadata"]["data_source_trust_status"] == "PASS"
    assert result["governance_metadata"]["model_scope"] == "SIMULATED_PROTOTYPE"


def test_api_gateway_forecast_success_after_data_source_trust_pass(tmp_path):
    import sys

    sys.path.insert(0, str(PROJECT_ROOT / "src"))
    from api_gateway import ApiGateway
    from artifact_repository import ArtifactRepository

    repository = ArtifactRepository(tmp_path / "transaction-store")

    response = ApiGateway(
        artifact_repository=repository,
        data_source_workspace=tmp_path / "data-source-attempts",
    ).handle_request(
        method="POST",
        path="/v1/predict/forecast",
        json_body={
            "input_context": "Run internal retention forecast.",
            "source_context": "CLI",
            "source": {
                "source_name": "approved-audit-log",
                "owner_approved": True,
                "consent_status": "APPROVED",
                "reliability_rating": 0.95,
                "data_age_days": 2,
            },
            "input_payload": {
                "baseline_risk": 0.3,
                "volatility": 0.1,
                "exposure": 0.2,
            },
        },
    )

    stored = repository.get_transaction(response["body"]["transaction_id"])

    assert response["status_code"] == 200
    assert response["body"]["success"] is True
    assert response["body"]["status"] == "COMPLETED"
    assert response["body"]["trust_result"]["status"] == "PASS"
    assert response["body"]["forecast"]["forecasted_risk_score"] == 0.45
    assert response["body"]["forecast"]["predicted_outcome"] == "LOW_RISK"
    assert stored["status"] == "FORECAST_COMPLETED"
    assert stored["transaction_metadata"]["workflow_step"] == "forecasting"
    assert stored["transaction_metadata"]["result"] == "completed"


def test_api_gateway_forecast_halts_when_data_source_consent_missing(tmp_path):
    import sys

    sys.path.insert(0, str(PROJECT_ROOT / "src"))
    from api_gateway import ApiGateway
    from artifact_repository import ArtifactRepository

    repository = ArtifactRepository(tmp_path / "transaction-store")

    response = ApiGateway(
        artifact_repository=repository,
        data_source_workspace=tmp_path / "data-source-attempts",
    ).handle_request(
        method="POST",
        path="/v1/predict/forecast",
        json_body={
            "input_context": "Run internal retention forecast.",
            "source_context": "CLI",
            "source": {
                "source_name": "missing-consent-log",
                "owner_approved": True,
                "consent_status": "MISSING",
                "reliability_rating": 0.95,
                "data_age_days": 2,
            },
            "input_payload": {"baseline_risk": 0.3},
        },
    )

    stored = repository.get_transaction(response["body"]["transaction_id"])

    assert response["status_code"] == 403
    assert response["body"]["success"] is False
    assert response["body"]["status"] == "HALTED"
    assert response["body"]["trust_result"]["status"] == "FAIL"
    assert response["body"]["trust_result"]["reason"] == "CONSENT_NOT_APPROVED"
    assert "forecast" not in response["body"]
    assert stored["status"] == "FORECAST_HALTED"
    assert stored["transaction_metadata"]["result"] == "halted"
    assert stored["transaction_metadata"]["trust_result"]["reason"] == "CONSENT_NOT_APPROVED"


def test_api_gateway_forecast_halts_when_data_source_stale(tmp_path):
    import sys

    sys.path.insert(0, str(PROJECT_ROOT / "src"))
    from api_gateway import ApiGateway
    from artifact_repository import ArtifactRepository

    repository = ArtifactRepository(tmp_path / "transaction-store")

    response = ApiGateway(
        artifact_repository=repository,
        data_source_workspace=tmp_path / "data-source-attempts",
    ).handle_request(
        method="POST",
        path="/v1/predict/forecast",
        json_body={
            "input_context": "Run internal retention forecast.",
            "source_context": "CLI",
            "source": {
                "source_name": "stale-audit-log",
                "owner_approved": True,
                "consent_status": "APPROVED",
                "reliability_rating": 0.95,
                "data_age_days": 45,
            },
            "input_payload": {"baseline_risk": 0.3},
        },
    )

    stored = repository.get_transaction(response["body"]["transaction_id"])

    assert response["status_code"] == 403
    assert response["body"]["success"] is False
    assert response["body"]["status"] == "HALTED"
    assert response["body"]["trust_result"]["status"] == "FLAGGED"
    assert response["body"]["trust_result"]["reason"] == "DATA_SOURCE_STALE"
    assert "forecast" not in response["body"]
    assert stored["status"] == "FORECAST_HALTED"
    assert stored["transaction_metadata"]["result"] == "halted"
    assert stored["transaction_metadata"]["trust_result"]["reason"] == "DATA_SOURCE_STALE"


def test_orchestrator_predict_workflow_logs_success_fail_and_flagged(tmp_path):
    import sys

    sys.path.insert(0, str(PROJECT_ROOT / "src"))
    from artifact_repository import ArtifactRepository
    from orchestrator import IntegrationOrchestrator

    repository = ArtifactRepository(tmp_path / "transaction-store")
    orchestrator = IntegrationOrchestrator(
        artifact_repository=repository,
        asset_workspace=tmp_path / "assets",
    )

    trusted_source = {
        "source_name": "approved-audit-log",
        "owner_approved": True,
        "consent_status": "APPROVED",
        "reliability_rating": 0.95,
        "data_age_days": 2,
    }
    missing_consent_source = {
        **trusted_source,
        "source_name": "missing-consent-log",
        "consent_status": "MISSING",
    }
    stale_source = {
        **trusted_source,
        "source_name": "stale-audit-log",
        "data_age_days": 45,
    }

    success = orchestrator.predict_workflow(
        input_context="Run internal retention forecast.",
        source_context="CLI",
        source=trusted_source,
        input_payload={"baseline_risk": 0.3, "volatility": 0.1, "exposure": 0.2},
    )
    failed = orchestrator.predict_workflow(
        input_context="Run internal retention forecast.",
        source_context="CLI",
        source=missing_consent_source,
        input_payload={"baseline_risk": 0.3},
    )
    flagged = orchestrator.predict_workflow(
        input_context="Run internal retention forecast.",
        source_context="CLI",
        source=stale_source,
        input_payload={"baseline_risk": 0.3},
    )

    success_manifest = repository.get_transaction(success["transaction_id"])
    failed_manifest = repository.get_transaction(failed["transaction_id"])
    flagged_manifest = repository.get_transaction(flagged["transaction_id"])

    assert success["status"] == "COMPLETED"
    assert success["service_call_order"] == [
        "policy_check",
        "data_source_trust",
        "forecasting_engine",
        "transaction_manifest",
    ]
    assert success_manifest["status"] == "FORECAST_COMPLETED"

    assert failed["status"] == "HALTED"
    assert failed["trust_result"]["status"] == "FAIL"
    assert failed_manifest["status"] == "FORECAST_HALTED"

    assert flagged["status"] == "HALTED"
    assert flagged["trust_result"]["status"] == "FLAGGED"
    assert flagged_manifest["status"] == "FORECAST_HALTED"
