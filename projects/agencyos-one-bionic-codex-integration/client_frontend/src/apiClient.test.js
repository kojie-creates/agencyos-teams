import { describe, expect, it, vi } from "vitest";
import { createApiClient } from "./apiClient.js";

describe("createApiClient", () => {
  it("sends the configured API key header", async () => {
    const fetchImpl = vi.fn().mockResolvedValue({
      status: 200,
      ok: true,
      json: async () => ({ success: true, status: "COMPLETED" })
    });
    const client = createApiClient({
      baseUrl: "http://localhost:8000",
      apiKey: "test-key",
      fetchImpl
    });

    await client.runDiagnostics();

    expect(fetchImpl).toHaveBeenCalledWith(
      "http://localhost:8000/v1/diagnose?input=Run+internal+health+diagnostics.&source_context=FRONTEND_CLIENT",
      {
        method: "GET",
        headers: {
          "X-API-KEY": "test-key"
        }
      }
    );
  });

  it("maps 401 responses to an auth failure state", async () => {
    const client = createApiClient({
      baseUrl: "http://localhost:8000",
      apiKey: "bad-key",
      fetchImpl: vi.fn().mockResolvedValue({
        status: 401,
        ok: false,
        json: async () => ({ success: false, error: "UNAUTHORIZED" })
      })
    });

    await expect(client.runForecast({ source: {}, inputPayload: {} })).rejects.toMatchObject({
      kind: "AUTH_FAILURE",
      userMessage: "API key was rejected. Check configuration and try again."
    });
  });

  it("maps 403 responses to a governance halt state", async () => {
    const client = createApiClient({
      baseUrl: "http://localhost:8000",
      apiKey: "test-key",
      fetchImpl: vi.fn().mockResolvedValue({
        status: 403,
        ok: false,
        json: async () => ({
          success: false,
          status: "HALTED",
          reason: "CONSENT_NOT_APPROVED"
        })
      })
    });

    await expect(client.runForecast({ source: {}, inputPayload: {} })).rejects.toMatchObject({
      kind: "GOVERNANCE_HALT",
      userMessage: "Governance halted the request. Review the returned policy or source status."
    });
  });

  it("posts forecast requests with source metadata and input payload", async () => {
    const fetchImpl = vi.fn().mockResolvedValue({
      status: 200,
      ok: true,
      json: async () => ({
        success: true,
        status: "COMPLETED",
        transaction_id: "txn-test"
      })
    });
    const client = createApiClient({
      baseUrl: "http://localhost:8000/",
      apiKey: "test-key",
      fetchImpl
    });

    await client.runForecast({
      source: { source_name: "approved-audit-log" },
      inputPayload: { baseline_risk: 0.3 }
    });

    expect(fetchImpl).toHaveBeenCalledWith(
      "http://localhost:8000/v1/predict/forecast",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-API-KEY": "test-key"
        },
        body: JSON.stringify({
          input_context: "Run internal retention forecast.",
          source_context: "FRONTEND_CLIENT",
          source: { source_name: "approved-audit-log" },
          input_payload: { baseline_risk: 0.3 }
        })
      }
    );
  });
});
