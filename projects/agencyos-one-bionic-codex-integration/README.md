# AgencyOS One Bionic Codex Integration API

This package documents the current prototype API contract for the AgencyOS One Bionic Codex integration.

The API supports governed workflow starts, policy checks, diagnostics, data-source validation, simulated external adapter calls, simulated forecasting, and transaction manifest retrieval through `/v1/*` endpoints.

## What Is Proven

- The FastAPI service wrapper accepts HTTP requests and forwards them into the existing internal `ApiGateway` contract.
- Every `/v1/*` request requires `X-API-KEY` before application logic runs.
- Policy checks can return `PASS`, `FLAGGED`, or `FAIL`.
- Data Source Trust can classify source metadata as trusted, failed, or flagged.
- Forecasting runs only after Policy Gate and Data Source Trust pass.
- Transaction manifests include SHA-256 hashes and simulated persistence metadata.
- Docker service files are present for local container packaging.

## Scope Boundary

This is a prototype consumption contract.

The API supports integration work under controlled local conditions. It does not provide production user management, OAuth, multi-tenancy, live external network execution, live data-quality enforcement, or durable database persistence.

## Local Run

Install service dependencies:

```text
pip install -r requirements.txt
```

Set the service API key and run the service:

```text
set AGENCYOS_API_KEY=agencyos-local-dev-key
set PYTHONPATH=src
uvicorn api_gateway:app --host 127.0.0.1 --port 8000
```

Example local API key:

```text
agencyos-local-dev-key
```

Every request must include:

```text
X-API-KEY: agencyos-local-dev-key
```

## Docker Run

Build the image when Docker Desktop is running:

```text
docker build -t agencyos-one-bionic-codex-integration:prototype .
```

Run the service:

```text
docker run --rm -p 8000:8000 -e AGENCYOS_API_KEY=agencyos-local-dev-key agencyos-one-bionic-codex-integration:prototype
```

## Core Endpoints

### `POST /v1/workflow/start`

Starts a governed workflow after API key auth and Policy Gate review.

Example body:

```json
{
  "goal": "Draft an internal onboarding charter.",
  "source_context": "FRONTEND_CLIENT"
}
```

Policy-blocking language, such as high-risk keywords or PII, returns `403`.

### `GET /v1/policy/check`

Checks a text input against the Policy Gate.

Example query:

```text
/v1/policy/check?input=Draft%20an%20internal%20runbook&source_context=FRONTEND_CLIENT
```

### `GET /v1/diagnose`

Runs simulated service diagnostics through the Policy Gate and records a transaction manifest when completed.

Example query:

```text
/v1/diagnose?input=Run%20internal%20health%20diagnostics&source_context=FRONTEND_CLIENT
```

### `POST /v1/data-source/validate`

Validates source metadata before downstream intelligence modules consume it.

Example body:

```json
{
  "input_context": "Validate audit source for forecasting.",
  "source_context": "FRONTEND_CLIENT",
  "source": {
    "source_name": "approved-audit-log",
    "owner_approved": true,
    "consent_status": "APPROVED",
    "reliability_rating": 0.95,
    "data_age_days": 2
  }
}
```

Missing consent returns `403`. Stale or low-reliability data returns a flagged response from the validation endpoint.

### `POST /v1/predict/forecast`

Runs a simulated forecast after API key auth, Policy Gate, and Data Source Trust pass.

Example body:

```json
{
  "input_context": "Run internal retention forecast.",
  "source_context": "FRONTEND_CLIENT",
  "source": {
    "source_name": "approved-audit-log",
    "owner_approved": true,
    "consent_status": "APPROVED",
    "reliability_rating": 0.95,
    "data_age_days": 2
  },
  "input_payload": {
    "baseline_risk": 0.3,
    "volatility": 0.1,
    "exposure": 0.2
  }
}
```

If Data Source Trust returns `FAIL` or `FLAGGED`, forecasting halts and returns `403`.

### `GET|POST /v1/external/{service}/{endpoint}`

Simulates an external adapter call after Policy Gate and credential-scope checks.

Required credential scope format:

```text
{service}:{endpoint}
```

### `GET /v1/transactions/{transaction_id}`

Retrieves a transaction manifest from the local artifact repository attached to the running gateway instance.

## Response Codes

| Code | Meaning |
| --- | --- |
| `200` | Request accepted and completed. |
| `202` | Data-source validation produced a flagged result. |
| `400` | Required input is missing or malformed for the internal route. |
| `401` | API key is missing or invalid. |
| `403` | Policy Gate, credential scope, Data Source Trust, or forecast gating halted execution. |
| `404` | Route or transaction was not found. |
| `500` | Internal workflow or manifest logging failed. |
| `502` | Simulated external adapter failure. |

## How To Consume

1. Start the local service with `uvicorn` or Docker.
2. Import `openapi.yaml` into the frontend team's API client generator or API testing tool.
3. Set the `X-API-KEY` header on every request.
4. Treat `401` as an auth boundary failure.
5. Treat `403` as a governance halt that should be shown as a review state, not retried blindly.
6. Store returned `transaction_id` values in the frontend state when audit retrieval is needed.
7. Use `client_example/frontend_usage.py` as a minimal request-handling reference.

## Consumer Team Next Steps

- Connect UI forms to the documented request bodies.
- Add user-facing states for auth failure, policy halt, data-source review, and successful transaction IDs.
- Decide where `AGENCYOS_API_KEY` will be configured for each environment.
- Replace simulated persistence with the selected database layer in a later backend milestone.
- Keep product copy bounded to the current contract: the API supports governed prototype workflows and simulated intelligence under local test conditions.
