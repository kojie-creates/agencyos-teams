import { useMemo, useState } from "react";
import { createApiClient } from "./apiClient.js";

const initialSource = {
  source_name: "approved-audit-log",
  owner_approved: true,
  consent_status: "APPROVED",
  reliability_rating: 0.95,
  data_age_days: 2
};

const initialForecastInput = {
  baseline_risk: 0.3,
  volatility: 0.1,
  exposure: 0.2
};

const idleSteps = [
  { label: "Awaiting Policy Gate", state: "idle" },
  { label: "Validating Data Sources", state: "idle" },
  { label: "Executing Forecast", state: "idle" }
];

export default function App() {
  const [apiUrl, setApiUrl] = useState("http://localhost:8000");
  const [apiKey, setApiKey] = useState("");
  const [goal, setGoal] = useState("Run internal retention forecast.");
  const [source, setSource] = useState(initialSource);
  const [forecastInput, setForecastInput] = useState(initialForecastInput);
  const [steps, setSteps] = useState(idleSteps);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [isRunning, setIsRunning] = useState(false);

  const apiClient = useMemo(
    () => createApiClient({ baseUrl: apiUrl, apiKey }),
    [apiUrl, apiKey]
  );

  async function startAnalysis() {
    setIsRunning(true);
    setResult(null);
    setError(null);
    setSteps([
      { label: "Awaiting Policy Gate", state: "active" },
      { label: "Validating Data Sources", state: "idle" },
      { label: "Executing Forecast", state: "idle" }
    ]);

    try {
      const diagnostics = await apiClient.runDiagnostics({
        input: "Run internal health diagnostics.",
        sourceContext: "FRONTEND_CLIENT"
      });
      setSteps([
        { label: "Awaiting Policy Gate", state: "done", detail: diagnostics.policy?.status },
        { label: "Validating Data Sources", state: "active" },
        { label: "Executing Forecast", state: "idle" }
      ]);

      const forecast = await apiClient.runForecast({
        inputContext: goal,
        sourceContext: "FRONTEND_CLIENT",
        source,
        inputPayload: forecastInput
      });
      setSteps([
        { label: "Awaiting Policy Gate", state: "done", detail: forecast.policy?.status },
        { label: "Validating Data Sources", state: "done", detail: forecast.trust_result?.status },
        { label: "Executing Forecast", state: "done", detail: forecast.forecast?.status }
      ]);
      setResult(forecast);
    } catch (caughtError) {
      setSteps((currentSteps) =>
        currentSteps.map((step) =>
          step.state === "active" ? { ...step, state: "blocked" } : step
        )
      );
      setError(caughtError);
    } finally {
      setIsRunning(false);
    }
  }

  function updateSource(field, value) {
    setSource((current) => ({ ...current, [field]: value }));
  }

  function updateForecastInput(field, value) {
    setForecastInput((current) => ({ ...current, [field]: Number(value) }));
  }

  const manifestId = result?.transaction_id;

  return (
    <main className="shell">
      <section className="workspace">
        <header className="page-header">
          <div>
            <p className="eyebrow">AgencyOS One API Consumer</p>
            <h1>Governed Analysis</h1>
          </div>
          <div className="service-pill">Local API Contract</div>
        </header>

        <div className="layout">
          <section className="panel controls-panel" aria-label="Analysis setup">
            <h2>Configuration</h2>
            <label>
              API URL
              <input value={apiUrl} onChange={(event) => setApiUrl(event.target.value)} />
            </label>
            <label>
              API Key
              <input
                value={apiKey}
                onChange={(event) => setApiKey(event.target.value)}
                placeholder="AGENCYOS_API_KEY"
                type="password"
              />
            </label>

            <h2>Workflow Trigger</h2>
            <label>
              Analysis goal
              <textarea value={goal} onChange={(event) => setGoal(event.target.value)} />
            </label>

            <div className="field-grid">
              <label>
                Source name
                <input
                  value={source.source_name}
                  onChange={(event) => updateSource("source_name", event.target.value)}
                />
              </label>
              <label>
                Consent
                <select
                  value={source.consent_status}
                  onChange={(event) => updateSource("consent_status", event.target.value)}
                >
                  <option value="APPROVED">APPROVED</option>
                  <option value="MISSING">MISSING</option>
                </select>
              </label>
              <label className="checkbox-row">
                <input
                  checked={source.owner_approved}
                  onChange={(event) => updateSource("owner_approved", event.target.checked)}
                  type="checkbox"
                />
                Owner approved
              </label>
              <label>
                Reliability
                <input
                  max="1"
                  min="0"
                  onChange={(event) => updateSource("reliability_rating", Number(event.target.value))}
                  step="0.01"
                  type="number"
                  value={source.reliability_rating}
                />
              </label>
              <label>
                Data age days
                <input
                  min="0"
                  onChange={(event) => updateSource("data_age_days", Number(event.target.value))}
                  type="number"
                  value={source.data_age_days}
                />
              </label>
            </div>

            <h2>Forecast Inputs</h2>
            <div className="field-grid">
              <label>
                Baseline risk
                <input
                  max="1"
                  min="0"
                  onChange={(event) => updateForecastInput("baseline_risk", event.target.value)}
                  step="0.01"
                  type="number"
                  value={forecastInput.baseline_risk}
                />
              </label>
              <label>
                Volatility
                <input
                  max="1"
                  min="0"
                  onChange={(event) => updateForecastInput("volatility", event.target.value)}
                  step="0.01"
                  type="number"
                  value={forecastInput.volatility}
                />
              </label>
              <label>
                Exposure
                <input
                  max="1"
                  min="0"
                  onChange={(event) => updateForecastInput("exposure", event.target.value)}
                  step="0.01"
                  type="number"
                  value={forecastInput.exposure}
                />
              </label>
            </div>

            <button disabled={isRunning || !apiKey.trim()} onClick={startAnalysis}>
              {isRunning ? "Running Analysis" : "Start New Analysis"}
            </button>
          </section>

          <section className="panel status-panel" aria-label="Analysis status">
            <h2>Status Visibility</h2>
            <ol className="steps">
              {steps.map((step) => (
                <li className={`step ${step.state}`} key={step.label}>
                  <span className="step-dot" />
                  <div>
                    <strong>{step.label}</strong>
                    {step.detail ? <span>{step.detail}</span> : null}
                  </div>
                </li>
              ))}
            </ol>

            {error ? (
              <div className="result-block error-block">
                <p>{error.userMessage}</p>
                <pre>{JSON.stringify(error.body, null, 2)}</pre>
              </div>
            ) : null}

            {result ? (
              <div className="result-block">
                <p>Analysis Complete. View Manifest ID {manifestId}.</p>
                <dl>
                  <div>
                    <dt>Forecast status</dt>
                    <dd>{result.forecast?.status}</dd>
                  </div>
                  <div>
                    <dt>Risk score</dt>
                    <dd>{result.forecast?.forecasted_risk_score}</dd>
                  </div>
                  <div>
                    <dt>Outcome</dt>
                    <dd>{result.forecast?.predicted_outcome}</dd>
                  </div>
                </dl>
                <pre>{JSON.stringify(result, null, 2)}</pre>
              </div>
            ) : (
              <div className="empty-state">
                Configure the API key, review inputs, then start an analysis.
              </div>
            )}
          </section>
        </div>
      </section>
    </main>
  );
}
