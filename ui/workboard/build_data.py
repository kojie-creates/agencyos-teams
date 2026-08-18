from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUNS_DIR = ROOT / ".agencyos-runtime" / "runs"
OUTPUT = Path(__file__).resolve().parent / "workboard-data.json"

STATUS_MAP = {
    "ready": "ready",
    "in_progress": "in_progress",
    "handoff_pending": "waiting",
    "under_review": "waiting",
    "evidence_required": "waiting",
    "awaiting_human": "waiting",
    "approved": "ready",
    "release_ready": "ready",
    "released": "completed",
    "closeout_pending": "ready",
    "closed": "completed",
    "rejected": "completed",
    "blocked": "waiting",
    "failed": "waiting",
    "cancelled": "completed",
    "received": "in_progress",
    "classified": "in_progress",
    "planned": "in_progress",
    "awaiting_dependencies": "in_progress",
    "dispatched": "in_progress",
    "intake_required": "in_progress",
}

STAGE_MAP = {
    "ready": "Ready",
    "in_progress": "Drafting",
    "waiting": "Approval",
    "completed": "Closed",
}


def title_from_run(data: dict) -> str:
    request = data.get("request") or {}
    return request.get("title") or data.get("project_id") or "Untitled work"


def summary_from_run(data: dict) -> str:
    request = data.get("request") or {}
    desired = request.get("requested_outcome") or request.get("title") or "AgencyOS project work"
    return desired[:110] + ("..." if len(desired) > 110 else "")


def model_from_run(data: dict) -> str:
    artifacts = data.get("artifacts") or []
    claims = []
    for artifact in artifacts:
        claims.extend(artifact.get("claims", []))
    for claim in claims:
        if "google/gemma-4-e4b" in claim:
            return "Gemma via LM Studio"
        if "openai_compatible_local" in claim:
            return "Local model"
    return "Gemma via LM Studio"


def artifact_summary(data: dict) -> str:
    artifacts = data.get("artifacts") or []
    if artifacts:
        first = artifacts[0]
        content = (first.get("content") or "")
        compact = " ".join(content.split())
        text = compact[:180]
        if len(compact) > 180:
            text += "..."
        return text or "Generated artifact for this work item."
    return "Generated artifact for this work item."


def build_item(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    request = data.get("request") or {}
    raw_state = data.get("state")
    status = STATUS_MAP.get(raw_state, "in_progress")
    project = data.get("project_id") or request.get("project_slug") or "AgencyOS"
    return {
        "id": data.get("run_id") or path.stem,
        "title": title_from_run(data),
        "project": project.replace("project-", "").replace("-", " ").title(),
        "summary": summary_from_run(data),
        "status": status,
        "stage": STAGE_MAP.get(status, "Drafting"),
        "time": "recent",
        "model": model_from_run(data),
        "tags": [request.get("action_class") or "Artifact", request.get("required_workstreams", ["research"])[0] if request.get("required_workstreams") else "research"],
        "artifactSummary": artifact_summary(data),
        "nextAction": "Open" if status in {"ready", "in_progress"} else "Review",
        "artifactPath": ((data.get("artifacts") or [{}])[0].get("path")) if data.get("artifacts") else "",
        "runId": data.get("run_id") or path.stem,
    }


def main() -> None:
    if not RUNS_DIR.exists():
        OUTPUT.write_text(json.dumps({"items": []}, indent=2), encoding="utf-8")
        return

    items = []
    for path in sorted(RUNS_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
        try:
            item = build_item(path)
        except Exception:
            continue
        items.append(item)

    payload = {"items": items[:12]}
    OUTPUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
