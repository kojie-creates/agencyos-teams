export function createApiClient({
  baseUrl = "http://localhost:8000",
  apiKey,
  fetchImpl = fetch
} = {}) {
  const normalizedBaseUrl = String(baseUrl || "").replace(/\/+$/, "");

  async function request(path, options = {}) {
    const response = await fetchImpl(`${normalizedBaseUrl}${path}`, {
      ...options,
      headers: {
        ...(options.headers || {}),
        "X-API-KEY": apiKey || ""
      }
    });
    const body = await response.json();

    if (response.ok) {
      return body;
    }

    throw mapApiError(response.status, body);
  }

  return {
    runDiagnostics({
      input = "Run internal health diagnostics.",
      sourceContext = "FRONTEND_CLIENT"
    } = {}) {
      const params = new URLSearchParams({
        input,
        source_context: sourceContext
      });
      return request(`/v1/diagnose?${params.toString()}`, {
        method: "GET"
      });
    },

    runForecast({
      inputContext = "Run internal retention forecast.",
      sourceContext = "FRONTEND_CLIENT",
      source,
      inputPayload
    }) {
      return request("/v1/predict/forecast", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          input_context: inputContext,
          source_context: sourceContext,
          source,
          input_payload: inputPayload
        })
      });
    }
  };
}

function mapApiError(status, body) {
  if (status === 401) {
    return {
      kind: "AUTH_FAILURE",
      status,
      body,
      userMessage: "API key was rejected. Check configuration and try again."
    };
  }

  if (status === 403) {
    return {
      kind: "GOVERNANCE_HALT",
      status,
      body,
      userMessage: "Governance halted the request. Review the returned policy or source status."
    };
  }

  return {
    kind: "REQUEST_FAILURE",
    status,
    body,
    userMessage: "The API request failed. Check the service and try again."
  };
}
