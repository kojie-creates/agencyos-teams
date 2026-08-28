"""Example client for the AgencyOS prototype API contract.

Run after starting the service:
    uvicorn api_gateway:app --host 127.0.0.1 --port 8000
"""

from __future__ import annotations

import os
from typing import Any

import requests


BASE_URL = os.getenv("AGENCYOS_API_URL", "http://127.0.0.1:8000")
API_KEY = os.getenv("AGENCYOS_API_KEY", "agencyos-local-dev-key")


def request_json(method: str, path: str, **kwargs: Any) -> dict[str, Any]:
    headers = kwargs.pop("headers", {})
    headers["X-API-KEY"] = API_KEY
    response = requests.request(
        method,
        f"{BASE_URL}{path}",
        headers=headers,
        timeout=10,
        **kwargs,
    )

    body = response.json()
    if response.status_code == 401:
        return {"handled_as": "AUTH_FAILURE", "body": body}
    if response.status_code == 403:
        return {"handled_as": "GOVERNANCE_HALT", "body": body}
    if response.status_code >= 400:
        return {"handled_as": "REQUEST_FAILURE", "body": body}
    return {"handled_as": "SUCCESS", "body": body}


def run_examples() -> None:
    successful_workflow = request_json(
        "POST",
        "/v1/workflow/start",
        json={
            "goal": "Draft an internal onboarding charter.",
            "source_context": "FRONTEND_CLIENT",
        },
    )
    print("successful_workflow", successful_workflow)

    policy_failure = request_json(
        "POST",
        "/v1/workflow/start",
        json={
            "goal": "Prepare acquisition plan for external send.",
            "source_context": "FRONTEND_CLIENT",
        },
    )
    print("policy_failure", policy_failure)

    diagnostics = request_json(
        "GET",
        "/v1/diagnose",
        params={
            "input": "Run internal health diagnostics.",
            "source_context": "FRONTEND_CLIENT",
        },
    )
    print("diagnostics", diagnostics)

    forecast = request_json(
        "POST",
        "/v1/predict/forecast",
        json={
            "input_context": "Run internal retention forecast.",
            "source_context": "FRONTEND_CLIENT",
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
    print("forecast", forecast)


if __name__ == "__main__":
    run_examples()
