"""Simulated forecasting engine gated by data-source trust results."""


class ForecastingEngine:
    """Runs controlled prototype predictions from validated source context."""

    def run_prediction(self, source_context: dict, input_payload: dict) -> dict:
        """Return a simulated forecast using validated data-source metadata."""
        trust_context = source_context or {}
        payload = input_payload or {}

        if trust_context.get("status") != "PASS":
            return {
                "status": "HALTED",
                "reason": "DATA_SOURCE_TRUST_REQUIRED",
                "required_action": "DATA_SOURCE_REVIEW",
                "governance_metadata": self._governance_metadata(trust_context),
            }

        forecasted_risk_score = self._risk_score(payload)
        predicted_outcome = self._predicted_outcome(forecasted_risk_score)

        return {
            "status": "PASS",
            "forecasted_risk_score": forecasted_risk_score,
            "predicted_outcome": predicted_outcome,
            "confidence_interval": {
                "lower_bound": round(max(0.0, forecasted_risk_score - 0.1), 2),
                "upper_bound": round(min(1.0, forecasted_risk_score + 0.1), 2),
            },
            "human_review_required": forecasted_risk_score >= 0.5,
            "governance_metadata": self._governance_metadata(trust_context),
        }

    def _risk_score(self, payload: dict) -> float:
        baseline_risk = float(payload.get("baseline_risk") or 0)
        volatility = float(payload.get("volatility") or 0)
        exposure = float(payload.get("exposure") or 0)
        score = baseline_risk + exposure - (volatility * 0.5)
        return round(min(1.0, max(0.0, score)), 2)

    def _predicted_outcome(self, forecasted_risk_score: float) -> str:
        if forecasted_risk_score >= 0.75:
            return "HIGH_RISK"
        if forecasted_risk_score >= 0.5:
            return "MODERATE_RISK"
        return "LOW_RISK"

    def _governance_metadata(self, source_context: dict) -> dict:
        return {
            "data_source_trust_status": source_context.get("status"),
            "data_source_trust_reason": source_context.get("reason"),
            "source_name": source_context.get("source_name", "unknown"),
            "model_scope": "SIMULATED_PROTOTYPE",
            "production_claim": False,
        }
