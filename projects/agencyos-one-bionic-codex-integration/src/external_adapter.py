"""Simulated external API adapter for controlled integration tests."""

from pathlib import Path


class ExternalAPIError(Exception):
    """Represents a simulated upstream API failure."""

    def __init__(self, error_code: str, message: str):
        super().__init__(message)
        self.error_code = error_code


class GenericAPIAdapter:
    """Executes simulated calls from an OpenAPI contract and scoped credentials."""

    def execute_call(
        self,
        service: str,
        endpoint: str,
        openapi_spec: str,
        credentials: dict,
        payload: dict | None = None,
    ) -> dict:
        """Return a JSON-safe simulated external call result."""
        spec_path = Path(openapi_spec)
        if not spec_path.is_file():
            raise ExternalAPIError("OPENAPI_SPEC_NOT_FOUND", "OpenAPI specification file not found.")

        if not credentials.get("token"):
            raise ExternalAPIError("MISSING_CREDENTIAL_TOKEN", "Credential token is required.")

        request_payload = payload or {}
        if request_payload.get("simulate_error"):
            error_code = str(request_payload["simulate_error"])
            raise ExternalAPIError(error_code, f"Simulated external API failure: {error_code}")

        spec_text = spec_path.read_text(encoding="utf-8")

        return {
            "status": "PASS",
            "service": str(service),
            "endpoint": str(endpoint),
            "credential_scope_verified": True,
            "openapi_contract_loaded": "openapi" in spec_text.lower(),
            "response": {
                "result": "SIMULATED_EXTERNAL_CALL_COMPLETE",
                "error_code": None,
            },
        }
