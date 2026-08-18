#!/usr/bin/env python3
"""Deterministic AgencyOS Teams enforcement kernel.

Priority 1 vertical slice: lifecycle enforcement, gated transitions, work
packet scheduling, evidence checks, human gate pauses, and replayable state.
"""

from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import urllib.request
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from agencyos.schemas import KernelRunSnapshot
from agencyos.policy_registry import PolicyOutcome, PolicyRegistry


SCHEMA_VERSION = "kernel.p1.v1"


class TransitionError(RuntimeError):
    """Raised when a lifecycle transition is not authorized."""


class LifecycleState(str, Enum):
    INTAKE_REQUIRED = "intake_required"
    RECEIVED = "received"
    CLASSIFIED = "classified"
    PLANNED = "planned"
    AWAITING_DEPENDENCIES = "awaiting_dependencies"
    READY = "ready"
    DISPATCHED = "dispatched"
    IN_PROGRESS = "in_progress"
    HANDOFF_PENDING = "handoff_pending"
    UNDER_REVIEW = "under_review"
    EVIDENCE_REQUIRED = "evidence_required"
    AWAITING_HUMAN = "awaiting_human"
    APPROVED = "approved"
    REJECTED = "rejected"
    BLOCKED = "blocked"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RELEASE_READY = "release_ready"
    RELEASED = "released"
    CLOSEOUT_PENDING = "closeout_pending"
    CLOSED = "closed"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ScopeClass(str, Enum):
    ONE_TASK = "one_task"
    ONE_PROJECT = "one_project"
    MULTIPLE_PROJECTS = "multiple_projects"
    ONGOING_OPERATING_SYSTEM = "ongoing_operating_system"


class GateDecision(str, Enum):
    PERMIT = "permit"
    HOLD = "hold"
    BLOCK = "block"
    ESCALATE = "escalate"


LEGAL_TRANSITIONS: dict[LifecycleState, set[LifecycleState]] = {
    LifecycleState.INTAKE_REQUIRED: {LifecycleState.RECEIVED, LifecycleState.CANCELLED},
    LifecycleState.RECEIVED: {LifecycleState.CLASSIFIED, LifecycleState.BLOCKED},
    LifecycleState.CLASSIFIED: {LifecycleState.PLANNED, LifecycleState.AWAITING_HUMAN, LifecycleState.BLOCKED},
    LifecycleState.PLANNED: {
        LifecycleState.AWAITING_DEPENDENCIES,
        LifecycleState.READY,
        LifecycleState.BLOCKED,
    },
    LifecycleState.AWAITING_DEPENDENCIES: {LifecycleState.READY, LifecycleState.BLOCKED},
    LifecycleState.READY: {LifecycleState.DISPATCHED, LifecycleState.AWAITING_HUMAN, LifecycleState.BLOCKED, LifecycleState.CANCELLED},
    LifecycleState.DISPATCHED: {LifecycleState.IN_PROGRESS, LifecycleState.FAILED},
    LifecycleState.IN_PROGRESS: {LifecycleState.HANDOFF_PENDING, LifecycleState.FAILED},
    LifecycleState.HANDOFF_PENDING: {
        LifecycleState.UNDER_REVIEW,
        LifecycleState.EVIDENCE_REQUIRED,
        LifecycleState.CLOSEOUT_PENDING,
        LifecycleState.APPROVED,
        LifecycleState.AWAITING_HUMAN,
        LifecycleState.BLOCKED,
    },
    LifecycleState.UNDER_REVIEW: {LifecycleState.APPROVED, LifecycleState.REJECTED, LifecycleState.EVIDENCE_REQUIRED},
    LifecycleState.EVIDENCE_REQUIRED: {LifecycleState.UNDER_REVIEW, LifecycleState.HANDOFF_PENDING},
    LifecycleState.AWAITING_HUMAN: {LifecycleState.APPROVED, LifecycleState.REJECTED},
    LifecycleState.APPROVED: {LifecycleState.RELEASE_READY, LifecycleState.CLOSEOUT_PENDING, LifecycleState.CLOSED, LifecycleState.BLOCKED},
    LifecycleState.REJECTED: {LifecycleState.CANCELLED, LifecycleState.BLOCKED},
    LifecycleState.BLOCKED: {LifecycleState.READY, LifecycleState.CANCELLED},
    LifecycleState.FAILED: {LifecycleState.READY, LifecycleState.CANCELLED},
    LifecycleState.RELEASE_READY: {LifecycleState.RELEASED},
    LifecycleState.RELEASED: {LifecycleState.CLOSEOUT_PENDING},
    LifecycleState.CLOSEOUT_PENDING: {LifecycleState.CLOSED, LifecycleState.EVIDENCE_REQUIRED},
    LifecycleState.CANCELLED: set(),
    LifecycleState.CLOSED: set(),
}


@dataclass
class KernelRequest:
    request_id: str
    title: str
    actor_id: str
    requested_outcome: str
    action_class: str
    reversible: bool
    external: bool
    sensitive: bool
    required_workstreams: list[str]
    dependencies: dict[str, list[str]] = field(default_factory=dict)
    evidence_required_for: list[str] = field(default_factory=list)
    existing_project_ref: str | None = None
    create_project: bool = False
    project_slug: str | None = None
    human_owner_id: str | None = None
    scope_class: ScopeClass = ScopeClass.ONE_PROJECT


@dataclass
class WorkPacket:
    workstream_id: str
    actor_id: str
    capability: str
    dependencies: list[str] = field(default_factory=list)
    state: LifecycleState = LifecycleState.READY
    artifact_id: str | None = None
    retries: int = 0
    max_retries: int = 1
    expected_output: str = "local artifact"
    required_evidence: list[str] = field(default_factory=list)
    pause_conditions: list[str] = field(default_factory=list)
    granted_permissions: list[str] = field(default_factory=list)
    withheld_permissions: list[str] = field(default_factory=list)


@dataclass
class Artifact:
    artifact_id: str
    workstream_id: str
    path: str
    content: str
    creator_id: str
    evidence_ids: list[str] = field(default_factory=list)
    verified_by: str | None = None
    claims: list[str] = field(default_factory=list)
    content_hash: str = ""


@dataclass
class EvidenceItem:
    evidence_id: str
    workstream_id: str
    path: str
    summary: str
    actor_id: str


@dataclass
class Handoff:
    handoff_id: str
    artifact_ids: list[str]
    complete: bool
    created_by: str


@dataclass
class RuntimeEvent:
    event_id: str
    run_id: str
    from_state: LifecycleState | None
    to_state: LifecycleState
    actor_id: str
    reason: str
    timestamp: str


@dataclass
class ApprovalRecord:
    approval_id: str
    approver_id: str
    decision: str
    rationale: str
    exact_action: str
    constraints: list[str]
    expires_at: str | None
    timestamp: str
    approved_artifact_hash: str | None = None


@dataclass
class PolicyDecisionRecord:
    decision_id: str
    policy_version: str
    actor_id: str
    requested_action: str
    resource: str
    risk_level: str
    outcome: str
    applicable_rules: list[str] = field(default_factory=list)
    required_conditions: list[str] = field(default_factory=list)
    missing_evidence: list[str] = field(default_factory=list)
    required_approval: str | None = None
    reason: str = ""
    timestamp: str = ""


@dataclass
class VerificationRecord:
    verification_id: str
    artifact_id: str
    verifier_id: str
    artifact_hash: str
    result: str
    timestamp: str


@dataclass
class ClaimRecord:
    claim_id: str
    artifact_id: str
    text: str
    evidence_status: str
    evidence_ids: list[str] = field(default_factory=list)
    claim_type: str = "general"
    required_approval: str | None = None


@dataclass
class ModelAdapterPolicy:
    enabled: bool = False
    allowed_models: list[str] = field(default_factory=list)
    api_key_env: str = "OPENAI_API_KEY"
    base_url: str = ""
    max_prompt_chars: int = 12000
    max_output_chars: int = 8000


@dataclass
class ModelCallRecord:
    model_call_id: str
    provider: str
    model: str
    actor_id: str
    workstream_id: str
    prompt_hash: str
    output_hash: str | None
    result: str
    error_message: str = ""
    artifact_id: str | None = None
    timestamp: str = ""


@dataclass
class FailurePacket:
    failure_id: str
    workstream_id: str
    actor_id: str
    error_type: str
    error_message: str
    retryable: bool
    retry_count: int
    resolution: str
    timestamp: str


@dataclass
class ReconciliationRecord:
    reconciliation_id: str
    artifact_ids: list[str]
    conflict_keys: list[str]
    state: str
    timestamp: str


@dataclass
class CloseoutRecord:
    closeout_id: str
    created_by: str
    artifact_ids: list[str]
    evidence_ids: list[str]
    timestamp: str


@dataclass
class LearningRecord:
    learning_id: str
    run_id: str
    project_id: str
    lesson: str
    timestamp: str


@dataclass
class KernelRun:
    run_id: str
    request: KernelRequest
    project_id: str
    state: LifecycleState
    risk_level: RiskLevel
    execution_mode: str
    execution_batches: list[list[str]] = field(default_factory=list)
    scope_class: ScopeClass = ScopeClass.ONE_PROJECT
    packets: list[WorkPacket] = field(default_factory=list)
    runnable_packets: list[WorkPacket] = field(default_factory=list)
    artifacts: list[Artifact] = field(default_factory=list)
    evidence: list[EvidenceItem] = field(default_factory=list)
    handoff: Handoff | None = None
    missing_evidence: list[str] = field(default_factory=list)
    block_reason: str = ""
    human_approval_by: str | None = None
    intake_required: list[str] = field(default_factory=list)
    approval_records: list[ApprovalRecord] = field(default_factory=list)
    policy_decisions: list[PolicyDecisionRecord] = field(default_factory=list)
    verification_records: list[VerificationRecord] = field(default_factory=list)
    claim_records: list[ClaimRecord] = field(default_factory=list)
    model_call_records: list[ModelCallRecord] = field(default_factory=list)
    failure_packets: list[FailurePacket] = field(default_factory=list)
    reconciliation_records: list[ReconciliationRecord] = field(default_factory=list)
    closeout_records: list[CloseoutRecord] = field(default_factory=list)
    learning_records: list[LearningRecord] = field(default_factory=list)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:12]}"


def _content_hash(content: str) -> str:
    return f"sha256:{hashlib.sha256(content.encode('utf-8')).hexdigest()}"


def _encode(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, list):
        return [_encode(item) for item in value]
    if isinstance(value, dict):
        return {key: _encode(item) for key, item in value.items()}
    return value


def _decode_run(data: dict[str, Any]) -> KernelRun:
    try:
        KernelRunSnapshot.model_validate(data)
    except ValidationError as exc:
        raise ValueError(f"schema_validation_error: {exc}") from exc
    request_data = dict(data["request"])
    if "scope_class" in request_data:
        request_data["scope_class"] = ScopeClass(request_data["scope_class"])
    request = KernelRequest(**request_data)
    packets = [
        WorkPacket(
            **{
                **packet,
                "state": LifecycleState(packet["state"]),
            }
        )
        for packet in data.get("packets", [])
    ]
    runnable_ids = {packet["workstream_id"] for packet in data.get("runnable_packets", [])}
    artifacts = [Artifact(**artifact) for artifact in data.get("artifacts", [])]
    evidence = [EvidenceItem(**item) for item in data.get("evidence", [])]
    handoff = Handoff(**data["handoff"]) if data.get("handoff") else None
    return KernelRun(
        run_id=data["run_id"],
        request=request,
        project_id=data["project_id"],
        state=LifecycleState(data["state"]),
        risk_level=RiskLevel(data["risk_level"]),
        execution_mode=data["execution_mode"],
        execution_batches=data.get("execution_batches", []),
        scope_class=ScopeClass(data.get("scope_class", ScopeClass.ONE_PROJECT.value)),
        packets=packets,
        runnable_packets=[packet for packet in packets if packet.workstream_id in runnable_ids],
        artifacts=artifacts,
        evidence=evidence,
        handoff=handoff,
        missing_evidence=data.get("missing_evidence", []),
        block_reason=data.get("block_reason", ""),
        human_approval_by=data.get("human_approval_by"),
        intake_required=data.get("intake_required", []),
        approval_records=[ApprovalRecord(**item) for item in data.get("approval_records", [])],
        policy_decisions=[PolicyDecisionRecord(**item) for item in data.get("policy_decisions", [])],
        verification_records=[VerificationRecord(**item) for item in data.get("verification_records", [])],
        claim_records=[ClaimRecord(**item) for item in data.get("claim_records", [])],
        model_call_records=[ModelCallRecord(**item) for item in data.get("model_call_records", [])],
        failure_packets=[FailurePacket(**item) for item in data.get("failure_packets", [])],
        reconciliation_records=[ReconciliationRecord(**item) for item in data.get("reconciliation_records", [])],
        closeout_records=[CloseoutRecord(**item) for item in data.get("closeout_records", [])],
        learning_records=[LearningRecord(**item) for item in data.get("learning_records", [])],
    )


def _decode_event(data: dict[str, Any]) -> RuntimeEvent:
    return RuntimeEvent(
        event_id=data["event_id"],
        run_id=data["run_id"],
        from_state=LifecycleState(data["from_state"]) if data.get("from_state") else None,
        to_state=LifecycleState(data["to_state"]),
        actor_id=data["actor_id"],
        reason=data["reason"],
        timestamp=data["timestamp"],
    )


class StateStore:
    def __init__(self, root: Path):
        self.root = root
        self.runtime_dir = root / ".agencyos-runtime"
        self.state_dir = self.runtime_dir / "runs"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.sqlite_path = self.runtime_dir / "runtime.sqlite3"
        self._init_sqlite()

    def save(self, run: KernelRun) -> None:
        path = self.state_dir / f"{run.run_id}.json"
        payload = _encode(asdict(run))
        payload["schema_version"] = SCHEMA_VERSION
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        self._upsert_run(run, payload)

    def load(self, run_id: str) -> KernelRun:
        db = sqlite3.connect(self.sqlite_path)
        try:
            row = db.execute(
                "select payload_json from runs where run_id = ?",
                (run_id,),
            ).fetchone()
        finally:
            db.close()
        if row:
            return _decode_run(json.loads(row[0]))
        path = self.state_dir / f"{run_id}.json"
        return _decode_run(json.loads(path.read_text(encoding="utf-8")))

    def append_event(self, event: RuntimeEvent) -> None:
        path = self.state_dir / f"{event.run_id}.events.jsonl"
        payload = _encode(asdict(event))
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload) + "\n")
        self._insert_event(event, payload)

    def events(self, run_id: str) -> list[RuntimeEvent]:
        path = self.state_dir / f"{run_id}.events.jsonl"
        if path.exists():
            return [_decode_event(json.loads(line)) for line in path.read_text(encoding="utf-8").splitlines()]
        db = sqlite3.connect(self.sqlite_path)
        try:
            rows = db.execute(
                """
                select payload_json
                from runtime_events
                where run_id = ?
                order by rowid
                """,
                (run_id,),
            ).fetchall()
        finally:
            db.close()
        return [_decode_event(json.loads(row[0])) for row in rows]

    def list_runs(self) -> list[dict[str, str]]:
        db = sqlite3.connect(self.sqlite_path)
        try:
            rows = db.execute(
                """
                select run_id, project_id, state, risk_level, updated_at
                from runs
                order by updated_at desc
                """
            ).fetchall()
        finally:
            db.close()
        return [
            {
                "run_id": row[0],
                "project_id": row[1],
                "state": row[2],
                "risk_level": row[3],
                "updated_at": row[4],
            }
            for row in rows
        ]

    def policy_decisions(self, run_id: str) -> list[dict[str, str | None]]:
        db = sqlite3.connect(self.sqlite_path)
        try:
            rows = db.execute(
                """
                select decision_id, policy_version, actor_id, requested_action, resource,
                       risk_level, outcome, required_approval, reason, timestamp
                from policy_decisions
                where run_id = ?
                order by rowid
                """,
                (run_id,),
            ).fetchall()
        finally:
            db.close()
        return [
            {
                "decision_id": row[0],
                "policy_version": row[1],
                "actor_id": row[2],
                "requested_action": row[3],
                "resource": row[4],
                "risk_level": row[5],
                "outcome": row[6],
                "required_approval": row[7],
                "reason": row[8],
                "timestamp": row[9],
            }
            for row in rows
        ]

    def claim_records(self, run_id: str) -> list[dict[str, Any]]:
        db = sqlite3.connect(self.sqlite_path)
        try:
            rows = db.execute(
                """
                select claim_id, artifact_id, text, evidence_status, evidence_ids_json,
                       claim_type, required_approval
                from claim_records
                where run_id = ?
                order by rowid
                """,
                (run_id,),
            ).fetchall()
        finally:
            db.close()
        return [
            {
                "claim_id": row[0],
                "artifact_id": row[1],
                "text": row[2],
                "evidence_status": row[3],
                "evidence_ids": json.loads(row[4]),
                "claim_type": row[5],
                "required_approval": row[6],
            }
            for row in rows
        ]

    def _init_sqlite(self) -> None:
        db = sqlite3.connect(self.sqlite_path)
        try:
            db.execute(
                """
                create table if not exists runs (
                    run_id text primary key,
                    project_id text not null,
                    state text not null,
                    risk_level text not null,
                    updated_at text not null,
                    payload_json text not null
                )
                """
            )
            db.execute(
                """
                create table if not exists runtime_events (
                    event_id text primary key,
                    run_id text not null,
                    from_state text,
                    to_state text not null,
                    actor_id text not null,
                    reason text not null,
                    timestamp text not null,
                    payload_json text not null
                )
                """
            )
            db.execute(
                """
                create table if not exists policy_decisions (
                    decision_id text primary key,
                    run_id text not null,
                    policy_version text not null,
                    actor_id text not null,
                    requested_action text not null,
                    resource text not null,
                    risk_level text not null,
                    outcome text not null,
                    required_approval text,
                    reason text not null,
                    timestamp text not null,
                    payload_json text not null
                )
                """
            )
            db.execute(
                """
                create table if not exists claim_records (
                    claim_id text primary key,
                    run_id text not null,
                    artifact_id text not null,
                    text text not null,
                    evidence_status text not null,
                    evidence_ids_json text not null,
                    claim_type text not null,
                    required_approval text,
                    payload_json text not null
                )
                """
            )
            columns = {
                row[1]
                for row in db.execute("pragma table_info(claim_records)").fetchall()
            }
            if "evidence_ids_json" not in columns:
                db.execute("alter table claim_records add column evidence_ids_json text not null default '[]'")
            db.commit()
        finally:
            db.close()

    def _upsert_run(self, run: KernelRun, payload: dict[str, Any]) -> None:
        db = sqlite3.connect(self.sqlite_path)
        try:
            db.execute(
                """
                insert into runs (run_id, project_id, state, risk_level, updated_at, payload_json)
                values (?, ?, ?, ?, ?, ?)
                on conflict(run_id) do update set
                    project_id=excluded.project_id,
                    state=excluded.state,
                    risk_level=excluded.risk_level,
                    updated_at=excluded.updated_at,
                    payload_json=excluded.payload_json
                """,
                (
                    run.run_id,
                    run.project_id,
                    run.state.value,
                    run.risk_level.value,
                    _now(),
                    json.dumps(payload),
                ),
            )
            for decision in run.policy_decisions:
                decision_payload = _encode(asdict(decision))
                db.execute(
                    """
                    insert or ignore into policy_decisions (
                        decision_id, run_id, policy_version, actor_id, requested_action,
                        resource, risk_level, outcome, required_approval, reason, timestamp, payload_json
                    )
                    values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        decision.decision_id,
                        run.run_id,
                        decision.policy_version,
                        decision.actor_id,
                        decision.requested_action,
                        decision.resource,
                        decision.risk_level,
                        decision.outcome,
                        decision.required_approval,
                        decision.reason,
                        decision.timestamp,
                        json.dumps(decision_payload),
                    ),
                )
            db.execute("delete from claim_records where run_id = ?", (run.run_id,))
            for claim in run.claim_records:
                claim_payload = _encode(asdict(claim))
                db.execute(
                    """
                    insert into claim_records (
                        claim_id, run_id, artifact_id, text, evidence_status,
                        evidence_ids_json, claim_type, required_approval, payload_json
                    )
                    values (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        claim.claim_id,
                        run.run_id,
                        claim.artifact_id,
                        claim.text,
                        claim.evidence_status,
                        json.dumps(claim.evidence_ids),
                        claim.claim_type,
                        claim.required_approval,
                        json.dumps(claim_payload),
                    ),
                )
            db.commit()
        finally:
            db.close()

    def _insert_event(self, event: RuntimeEvent, payload: dict[str, Any]) -> None:
        db = sqlite3.connect(self.sqlite_path)
        try:
            db.execute(
                """
                insert or ignore into runtime_events (
                    event_id, run_id, from_state, to_state, actor_id, reason, timestamp, payload_json
                )
                values (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event.event_id,
                    event.run_id,
                    event.from_state.value if event.from_state else None,
                    event.to_state.value,
                    event.actor_id,
                    event.reason,
                    event.timestamp,
                    json.dumps(payload),
                ),
            )
            db.commit()
        finally:
            db.close()


class LocalFilesystemAdapter:
    def __init__(self, root: Path):
        self.root = root.resolve()

    def write_artifact(self, run_id: str, requested_path: str, content: str) -> str:
        artifact_root = (self.root / ".agencyos-runtime" / "artifacts" / run_id).resolve()
        target = (artifact_root / requested_path).resolve()
        if not target.is_relative_to(artifact_root):
            raise TransitionError("Artifact path is outside runtime artifact root.")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return target.relative_to(self.root).as_posix()


class LocalModelDraftClient:
    provider = "local_model_draft"

    def generate(self, model: str, prompt: str) -> str:
        return f"[{model} draft]\n\n{prompt.strip()}"


class OpenAICompatibleResponsesClient:
    provider = "openai_compatible"

    def __init__(self, provider: str, base_url: str, api_key: str, max_output_chars: int):
        self.provider = provider
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.max_output_chars = max_output_chars

    def generate(self, model: str, prompt: str) -> str:
        payload = json.dumps(
            {
                "model": model,
                "input": prompt,
                "max_output_tokens": self.max_output_chars,
            }
        ).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        request = urllib.request.Request(
            f"{self.base_url}/responses",
            data=payload,
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=60) as response:
            data = json.loads(response.read().decode("utf-8"))
        if data.get("output_text"):
            return data["output_text"]
        text_parts = []
        for item in data.get("output", []):
            for content in item.get("content", []):
                if content.get("type") in {"output_text", "text"} and content.get("text"):
                    text_parts.append(content["text"])
        if text_parts:
            return "\n".join(text_parts)
        raise TransitionError("Model response did not include output text.")


class OpenAIResponsesClient(OpenAICompatibleResponsesClient):
    def __init__(self, api_key: str, max_output_chars: int):
        super().__init__("openai", "https://api.openai.com/v1", api_key, max_output_chars)


class RuntimeConfig:
    def __init__(self, root: Path):
        self.root = root
        self.path = root / ".agencyos-runtime" / "config.local.json"
        self.data = self._load()

    def _load(self) -> dict[str, Any]:
        if not self.path.exists():
            return {}
        return json.loads(self.path.read_text(encoding="utf-8"))

    def model_policy(self, provider: str) -> ModelAdapterPolicy:
        if provider == "local_model_draft":
            return ModelAdapterPolicy(enabled=True, allowed_models=[], api_key_env="")
        data = self.data.get("model_adapters", {}).get(provider, {})
        return ModelAdapterPolicy(
            enabled=bool(data.get("enabled", False)),
            allowed_models=list(data.get("allowed_models", [])),
            api_key_env=data.get("api_key_env", "OPENAI_API_KEY"),
            base_url=data.get("base_url", ""),
            max_prompt_chars=int(data.get("max_prompt_chars", 12000)),
            max_output_chars=int(data.get("max_output_chars", 8000)),
        )


class Router:
    actor_by_workstream = {
        "research": "being-atlas",
        "build": "being-bob",
        "operate": "being-maya",
        "evidence": "being-vera",
        "audit": "being-vera",
        "verify": "being-truth",
        "closeout": "being-jaavis",
        "intake": "being-jaavis",
    }

    def classify_risk(self, request: KernelRequest) -> RiskLevel:
        if request.external and request.sensitive and not request.reversible:
            return RiskLevel.HIGH
        if request.sensitive or not request.reversible:
            return RiskLevel.HIGH
        if request.external:
            return RiskLevel.MEDIUM
        return RiskLevel.LOW

    def create_packets(self, request: KernelRequest) -> list[WorkPacket]:
        return [
            WorkPacket(
                workstream_id=workstream,
                actor_id=self.actor_by_workstream.get(workstream, f"specialist-{workstream}"),
                capability=f"{workstream}:artifact_creation",
                dependencies=request.dependencies.get(workstream, []),
                expected_output=f"{workstream} artifact",
                required_evidence=["source_or_validation"] if workstream in request.evidence_required_for else [],
                pause_conditions=["missing_evidence"] if workstream in request.evidence_required_for else [],
                granted_permissions=["read_context", "write_local_artifact"],
                withheld_permissions=["external_send", "destructive_change", "payment_action"],
            )
            for workstream in request.required_workstreams
        ]


class ProjectResolver:
    def __init__(self, root: Path):
        self.root = root

    def resolve(self, request: KernelRequest) -> tuple[str, list[str]]:
        if request.existing_project_ref:
            return request.existing_project_ref, []

        if request.create_project:
            if not request.human_owner_id or not request.human_owner_id.startswith("human-"):
                return "", ["human_owner_id"]
            slug = request.project_slug or request.request_id
            return f"project-{slug}", []

        first_run = self.root / ".first-run.json"
        if first_run.exists():
            data = json.loads(first_run.read_text(encoding="utf-8"))
            if data.get("project_id"):
                return data["project_id"], []

        return f"project-{request.request_id}", []


class DependencyEvaluator:
    def has_cycle(self, dependencies: dict[str, list[str]]) -> bool:
        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(node: str) -> bool:
            if node in visiting:
                return True
            if node in visited:
                return False
            visiting.add(node)
            for dep in dependencies.get(node, []):
                if visit(dep):
                    return True
            visiting.remove(node)
            visited.add(node)
            return False

        return any(visit(node) for node in dependencies)

    def runnable(self, packets: list[WorkPacket], completed: set[str]) -> list[WorkPacket]:
        return [
            packet
            for packet in packets
            if packet.state == LifecycleState.READY
            and packet.artifact_id is None
            and all(dep in completed for dep in packet.dependencies)
        ]

    def batches(self, packets: list[WorkPacket]) -> list[list[str]]:
        remaining = {packet.workstream_id: packet for packet in packets}
        completed: set[str] = set()
        batches = []
        while remaining:
            batch = [
                packet.workstream_id
                for packet in packets
                if packet.workstream_id in remaining
                and all(dep in completed for dep in packet.dependencies)
            ]
            if not batch:
                return []
            batches.append(batch)
            completed.update(batch)
            for workstream_id in batch:
                remaining.pop(workstream_id, None)
        return batches


class Scheduler:
    execution_mode = "deterministic_batches"

    def __init__(self, dependency_evaluator: DependencyEvaluator):
        self.dependency_evaluator = dependency_evaluator

    def plan(self, request: KernelRequest, packets: list[WorkPacket]) -> tuple[LifecycleState, list[WorkPacket], str, list[list[str]]]:
        if self.dependency_evaluator.has_cycle(request.dependencies):
            return LifecycleState.BLOCKED, [], "Dependency cycle detected.", []
        runnable = self.dependency_evaluator.runnable(packets, completed=set())
        batches = self.dependency_evaluator.batches(packets)
        if runnable:
            return LifecycleState.READY, runnable, "", batches
        return LifecycleState.AWAITING_DEPENDENCIES, [], "", batches


class Dispatcher:
    def dispatch(self, run: KernelRun) -> None:
        for packet in run.runnable_packets:
            if packet.state == LifecycleState.READY:
                packet.state = LifecycleState.DISPATCHED


class HandoffManager:
    def create(self, run: KernelRun, actor_id: str) -> Handoff:
        artifact_ids = [artifact.artifact_id for artifact in run.artifacts]
        complete = len(artifact_ids) == len(run.packets)
        return Handoff(
            handoff_id=_new_id("handoff"),
            artifact_ids=artifact_ids,
            complete=complete,
            created_by=actor_id,
        )


class GateEvaluator:
    def missing_evidence(self, run: KernelRun) -> list[str]:
        missing = []
        evidence_by_workstream = {item.workstream_id for item in run.evidence}
        for workstream in run.request.evidence_required_for:
            if workstream not in evidence_by_workstream:
                missing.append(workstream)
        return missing

    def release_decision(self, run: KernelRun, actor_id: str) -> GateDecision:
        if run.risk_level == RiskLevel.HIGH and run.human_approval_by != actor_id:
            return GateDecision.HOLD
        if run.state != LifecycleState.APPROVED:
            return GateDecision.BLOCK
        return GateDecision.PERMIT


class ReconciliationManager:
    def reconcile(self, run: KernelRun) -> ReconciliationRecord:
        values_by_key: dict[str, set[str]] = {}
        for artifact in run.artifacts:
            for claim in artifact.claims:
                if "=" not in claim:
                    continue
                key, value = claim.split("=", 1)
                values_by_key.setdefault(key.strip(), set()).add(value.strip())
        for claim in run.claim_records:
            if claim.evidence_status == "unclassified":
                continue
            key = f"claim_status:{claim.text.strip().lower()}"
            values_by_key.setdefault(key, set()).add(claim.evidence_status.strip().lower())
        conflict_keys = sorted(key for key, values in values_by_key.items() if len(values) > 1)
        record = ReconciliationRecord(
            reconciliation_id=_new_id("reconciliation"),
            artifact_ids=[artifact.artifact_id for artifact in run.artifacts],
            conflict_keys=conflict_keys,
            state="awaiting_human_decision" if conflict_keys else "no_conflicts_detected",
            timestamp=_now(),
        )
        run.reconciliation_records.append(record)
        return record


class CloseoutManager:
    def can_close(self, run: KernelRun, gate_evaluator: GateEvaluator) -> tuple[bool, list[str]]:
        missing = gate_evaluator.missing_evidence(run)
        if missing:
            return False, missing
        if not run.handoff or not run.handoff.complete:
            return False, ["handoff"]
        return True, []


class LearningRecorder:
    def record(self, run: KernelRun) -> LearningRecord:
        record = LearningRecord(
            learning_id=_new_id("learning"),
            run_id=run.run_id,
            project_id=run.project_id,
            lesson="generated_text_is_not_completion",
            timestamp=_now(),
        )
        run.learning_records.append(record)
        return record


class EnforcementKernel:
    def __init__(self, root: Path):
        self.root = root
        self.store = StateStore(root)
        self.project_resolver = ProjectResolver(root)
        self.router = Router()
        self.dependency_evaluator = DependencyEvaluator()
        self.scheduler = Scheduler(self.dependency_evaluator)
        self.dispatcher = Dispatcher()
        self.handoff_manager = HandoffManager()
        self.gate_evaluator = GateEvaluator()
        self.reconciliation_manager = ReconciliationManager()
        self.closeout_manager = CloseoutManager()
        self.learning_recorder = LearningRecorder()
        self.policy_registry = PolicyRegistry.default()
        self.local_filesystem = LocalFilesystemAdapter(root)
        self.model_client = LocalModelDraftClient()
        self.runtime_config = RuntimeConfig(root)

    def start_plain_text(self, text: str, actor_id: str, human_owner_id: str) -> KernelRun:
        intake_required = []
        if not text.strip():
            intake_required.append("requested_outcome")
        if len(text.strip().split()) < 8:
            intake_required.append("requested_outcome")
        intake_required.append("required_workstreams")
        request = KernelRequest(
            request_id=_new_id("request"),
            title="Plain language intake",
            actor_id=actor_id,
            requested_outcome=text.strip(),
            action_class="intake",
            reversible=True,
            external=False,
            sensitive=False,
            required_workstreams=[],
            human_owner_id=human_owner_id,
        )
        run = KernelRun(
            run_id=_new_id("run"),
            request=request,
            project_id=f"project-{request.request_id}",
            state=LifecycleState.INTAKE_REQUIRED,
            risk_level=RiskLevel.LOW,
            execution_mode=self.scheduler.execution_mode,
            intake_required=sorted(set(intake_required)),
        )
        self._record(run, None, LifecycleState.INTAKE_REQUIRED, actor_id, "plain language intake needs required fields")
        self.store.save(run)
        return run

    def start(self, request: KernelRequest) -> KernelRun:
        project_id, intake_required = self.project_resolver.resolve(request)
        run = KernelRun(
            run_id=_new_id("run"),
            request=request,
            project_id=project_id or f"project-{request.request_id}",
            state=LifecycleState.RECEIVED,
            risk_level=RiskLevel.LOW,
            execution_mode=self.scheduler.execution_mode,
            scope_class=request.scope_class,
            intake_required=intake_required,
        )
        if intake_required:
            run.state = LifecycleState.INTAKE_REQUIRED
            self._record(run, None, LifecycleState.INTAKE_REQUIRED, request.actor_id, "project creation needs human owner")
            self.store.save(run)
            return run
        self._record(run, None, LifecycleState.RECEIVED, request.actor_id, "request received")
        run.risk_level = self.router.classify_risk(request)
        self._transition_run(run, LifecycleState.CLASSIFIED, request.actor_id, "scope and risk classified")

        if run.risk_level == RiskLevel.HIGH:
            self._transition_run(run, LifecycleState.AWAITING_HUMAN, request.actor_id, "human approval required")
            self.store.save(run)
            return run

        run.packets = self.router.create_packets(request)
        self._transition_run(run, LifecycleState.PLANNED, request.actor_id, "work packets planned")
        planned_state, runnable, block_reason, batches = self.scheduler.plan(request, run.packets)
        run.runnable_packets = runnable
        run.execution_batches = batches
        run.block_reason = block_reason
        self._transition_run(run, planned_state, request.actor_id, block_reason or "scheduler evaluated dependencies")
        self.store.save(run)
        return run

    def transition(self, run_id: str, to_state: LifecycleState, actor_id: str, reason: str = "manual transition") -> KernelRun:
        run = self.store.load(run_id)
        self._transition_run(run, to_state, actor_id, reason)
        self.store.save(run)
        return run

    def dispatch_ready(self, run_id: str) -> KernelRun:
        run = self.store.load(run_id)
        if run.state != LifecycleState.READY:
            raise TransitionError(f"Cannot dispatch from {run.state.value}.")
        self._enforce_dispatch_policies(run)
        self.dispatcher.dispatch(run)
        self._transition_run(run, LifecycleState.DISPATCHED, run.request.actor_id, "runnable work dispatched")
        self._transition_run(run, LifecycleState.IN_PROGRESS, run.request.actor_id, "work in progress")
        self.store.save(run)
        return run

    def _enforce_dispatch_policies(self, run: KernelRun) -> None:
        for packet in run.runnable_packets:
            action = self._policy_action(packet)
            decision = self.policy_registry.evaluate(
                actor_id=packet.actor_id,
                actor_roles=self._actor_roles(packet),
                action=action,
                resource=packet.workstream_id,
                risk_level=run.risk_level.value,
                evidence_ids=[],
                approval_ids=[record.approval_id for record in run.approval_records],
            )
            self._record_policy_decision(run, decision)
            if decision.outcome == PolicyOutcome.PERMIT:
                continue
            run.block_reason = decision.reason
            if decision.outcome == PolicyOutcome.HOLD:
                self._transition_run(run, LifecycleState.AWAITING_HUMAN, packet.actor_id, decision.reason)
                self.store.save(run)
                raise TransitionError(decision.reason)
            self._transition_run(run, LifecycleState.BLOCKED, packet.actor_id, decision.reason)
            self.store.save(run)
            raise TransitionError(decision.reason)

    def _actor_roles(self, packet: WorkPacket) -> list[str]:
        if packet.actor_id.startswith("being-"):
            return [packet.actor_id.removeprefix("being-"), packet.workstream_id]
        if packet.actor_id.startswith("specialist-"):
            return [packet.workstream_id]
        return [packet.workstream_id]

    def _policy_action(self, packet: WorkPacket) -> str:
        if packet.capability.endswith(":artifact_creation"):
            return "write_local_artifact"
        if packet.capability.startswith("tool:"):
            return "tool_use"
        return packet.capability.split(":", 1)[0]

    def _looks_sensitive_evidence(self, path: str, summary: str) -> bool:
        value = f"{path} {summary}".lower()
        markers = ["sensitive", "client", "spend", "rent", "tenant", "proprietary", "secret"]
        return any(marker in value for marker in markers)

    def _reviewer_roles(self, reviewer_id: str) -> list[str]:
        if "truth" in reviewer_id or "verifier" in reviewer_id:
            return ["verifier", "truth"]
        if "vera" in reviewer_id or "evidence" in reviewer_id:
            return ["evidence", "verifier"]
        return ["verifier"]

    def _blocking_claim(self, run: KernelRun, artifact: Artifact) -> str | None:
        acceptable = {"VERIFIED", "SUPPORTED"}
        records = [record for record in run.claim_records if record.artifact_id == artifact.artifact_id]
        if records:
            for record in records:
                if record.evidence_status.upper() == "UNCLASSIFIED":
                    continue
                if record.evidence_status.upper() not in acceptable:
                    return record.text
            return None
        for claim in artifact.claims:
            if "::" not in claim:
                continue
            status, text = claim.split("::", 1)
            if status.strip().upper() not in acceptable:
                return text.strip() or claim
        return None

    def _claim_records_from_strings(self, artifact_id: str, claims: list[str]) -> list[ClaimRecord]:
        records = []
        for claim in claims:
            if "::" in claim:
                status, text = claim.split("::", 1)
                evidence_status = status.strip().lower()
                claim_text = text.strip()
            else:
                evidence_status = "unclassified"
                claim_text = claim.strip()
            if not claim_text:
                continue
            records.append(
                ClaimRecord(
                    claim_id=_new_id("claim"),
                    artifact_id=artifact_id,
                    text=claim_text,
                    evidence_status=evidence_status,
                )
            )
        return records

    def _matching_claim_ids_from_summary(self, claims: list[ClaimRecord], summary: str) -> set[str]:
        normalized_summary = " ".join(summary.lower().split())
        return {
            claim.claim_id
            for claim in claims
            if claim.text and " ".join(claim.text.lower().split()) in normalized_summary
        }

    def complete_artifact(
        self,
        run_id: str,
        workstream_id: str,
        path: str,
        content: str,
        actor_id: str,
        claims: list[str] | None = None,
    ) -> KernelRun:
        run = self.store.load(run_id)
        packet = self._packet(run, workstream_id)
        stored_path = self.local_filesystem.write_artifact(run_id, path, content)
        artifact = self.make_artifact(workstream_id, stored_path, content, actor_id, claims=claims)
        packet.artifact_id = artifact.artifact_id
        packet.state = LifecycleState.HANDOFF_PENDING
        run.artifacts.append(artifact)
        run.claim_records.extend(self._claim_records_from_strings(artifact.artifact_id, artifact.claims))
        if len(run.artifacts) == len(run.packets):
            self._transition_run(run, LifecycleState.HANDOFF_PENDING, actor_id, "all artifacts ready for handoff")
        self.store.save(run)
        return run

    def draft_model_artifact(
        self,
        run_id: str,
        workstream_id: str,
        path: str,
        prompt: str,
        model: str,
        actor_id: str,
        model_client: Any | None = None,
        provider: str = "local_model_draft",
    ) -> KernelRun:
        run = self.store.load(run_id)
        prompt_hash = _content_hash(prompt)

        def record_failure(error_type: str, error_message: str) -> None:
            current = self.store.load(run_id)
            current.model_call_records.append(
                ModelCallRecord(
                    model_call_id=_new_id("model-call"),
                    provider=provider,
                    model=model,
                    actor_id=actor_id,
                    workstream_id=workstream_id,
                    prompt_hash=prompt_hash,
                    output_hash=None,
                    result="failure",
                    error_message=error_message,
                    artifact_id=None,
                    timestamp=_now(),
                )
            )
            current.failure_packets.append(
                FailurePacket(
                    failure_id=_new_id("failure"),
                    workstream_id=workstream_id,
                    actor_id=actor_id,
                    error_type=error_type,
                    error_message=error_message,
                    retryable=False,
                    retry_count=0,
                    resolution="blocked",
                    timestamp=_now(),
                )
            )
            self.store.save(current)

        if run.request.sensitive or run.request.external:
            message = "Model adapter requires non-sensitive internal work."
            record_failure("model_policy_error", message)
            raise TransitionError(message)
        policy = self.runtime_config.model_policy(provider)
        if not policy.enabled:
            message = f"Model provider {provider} is not enabled."
            record_failure("model_policy_error", message)
            raise TransitionError(message)
        if policy.allowed_models and "*" not in policy.allowed_models and model not in policy.allowed_models:
            message = f"Model {model} is not allowed for provider {provider}."
            record_failure("model_policy_error", message)
            raise TransitionError(message)
        if len(prompt) > policy.max_prompt_chars:
            message = f"Prompt exceeds max_prompt_chars for provider {provider}."
            record_failure("model_policy_error", message)
            raise TransitionError(message)
        if model_client:
            client = model_client
        elif provider == "openai":
            api_key = os.getenv(policy.api_key_env)
            if not api_key:
                message = f"{policy.api_key_env} is not configured."
                record_failure("model_policy_error", message)
                raise TransitionError(message)
            client = OpenAIResponsesClient(api_key, policy.max_output_chars)
        elif policy.base_url:
            api_key = os.getenv(policy.api_key_env) if policy.api_key_env else ""
            client = OpenAICompatibleResponsesClient(provider, policy.base_url, api_key, policy.max_output_chars)
        else:
            client = self.model_client
        call_provider = getattr(client, "provider", provider)
        try:
            content = client.generate(model, prompt)
        except Exception as exc:
            message = str(exc) or exc.__class__.__name__
            provider = call_provider
            record_failure("model_adapter_error", message)
            raise TransitionError(message) from exc
        provider = call_provider
        claims = [f"SUPPORTED::Model draft generated by {provider}/{model}."]
        completed = self.complete_artifact(run_id, workstream_id, path, content, actor_id=actor_id, claims=claims)
        artifact = completed.artifacts[-1]
        completed.model_call_records.append(
            ModelCallRecord(
                model_call_id=_new_id("model-call"),
                provider=provider,
                model=model,
                actor_id=actor_id,
                workstream_id=workstream_id,
                prompt_hash=prompt_hash,
                output_hash=artifact.content_hash,
                result="success",
                error_message="",
                artifact_id=artifact.artifact_id,
                timestamp=_now(),
            )
        )
        self.store.save(completed)
        return completed

    def make_artifact(
        self,
        workstream_id: str,
        path: str,
        content: str,
        actor_id: str,
        claims: list[str] | None = None,
    ) -> Artifact:
        return Artifact(
            artifact_id=_new_id("artifact"),
            workstream_id=workstream_id,
            path=path,
            content=content,
            creator_id=actor_id,
            claims=claims or [],
            content_hash=_content_hash(content),
        )

    def make_approval_record(
        self,
        approver_id: str,
        decision: str,
        rationale: str,
        exact_action: str,
        constraints: list[str] | None = None,
        expires_at: str | None = None,
        approved_artifact_hash: str | None = None,
    ) -> ApprovalRecord:
        return ApprovalRecord(
            approval_id=_new_id("approval"),
            approver_id=approver_id,
            decision=decision,
            rationale=rationale,
            exact_action=exact_action,
            constraints=constraints or [],
            expires_at=expires_at,
            timestamp=_now(),
            approved_artifact_hash=approved_artifact_hash,
        )

    def create_handoff(self, run_id: str, actor_id: str) -> KernelRun:
        run = self.store.load(run_id)
        if run.state != LifecycleState.HANDOFF_PENDING:
            raise TransitionError(f"Cannot create handoff from {run.state.value}.")
        run.handoff = self.handoff_manager.create(run, actor_id)
        self.reconciliation_manager.reconcile(run)
        self.store.save(run)
        return run

    def request_closeout(self, run_id: str, actor_id: str) -> KernelRun:
        run = self.store.load(run_id)
        self._enforce_material_action(run, actor_id, ["operator"], "closeout", run.project_id)
        can_close, missing = self.closeout_manager.can_close(run, self.gate_evaluator)
        run.missing_evidence = missing
        if not can_close:
            self._transition_run(run, LifecycleState.EVIDENCE_REQUIRED, actor_id, "closeout blocked by missing evidence")
            self.store.save(run)
            return run
        if run.state == LifecycleState.APPROVED:
            self._transition_run(run, LifecycleState.CLOSED, actor_id, "closeout complete")
        else:
            self._transition_run(run, LifecycleState.CLOSEOUT_PENDING, actor_id, "closeout pending approval")
            self._transition_run(run, LifecycleState.CLOSED, actor_id, "closeout complete")
        run.closeout_records.append(
            CloseoutRecord(
                closeout_id=_new_id("closeout"),
                created_by=actor_id,
                artifact_ids=[artifact.artifact_id for artifact in run.artifacts],
                evidence_ids=[item.evidence_id for item in run.evidence],
                timestamp=_now(),
            )
        )
        self.learning_recorder.record(run)
        self.store.save(run)
        return run

    def attach_evidence(
        self,
        run_id: str,
        workstream_id: str,
        path: str,
        summary: str,
        actor_id: str,
        claim_ids: list[str] | None = None,
    ) -> KernelRun:
        run = self.store.load(run_id)
        targeted_claim_ids = set(claim_ids or [])
        existing_claim_ids = {claim.claim_id for claim in run.claim_records}
        unknown_claim_ids = targeted_claim_ids - existing_claim_ids
        if unknown_claim_ids:
            raise TransitionError(f"Unknown claim ids: {', '.join(sorted(unknown_claim_ids))}")
        action = "attach_sensitive_evidence" if self._looks_sensitive_evidence(path, summary) else "attach_evidence"
        self._enforce_material_action(run, actor_id, ["evidence"], action, workstream_id)
        evidence = EvidenceItem(
            evidence_id=_new_id("evidence"),
            workstream_id=workstream_id,
            path=path,
            summary=summary,
            actor_id=actor_id,
        )
        run.evidence.append(evidence)
        for artifact in run.artifacts:
            if artifact.workstream_id == workstream_id:
                artifact.evidence_ids.append(evidence.evidence_id)
                artifact_claims = [
                    claim for claim in run.claim_records if claim.artifact_id == artifact.artifact_id
                ]
                summary_claim_ids = self._matching_claim_ids_from_summary(artifact_claims, summary)
                for claim in run.claim_records:
                    if claim.artifact_id != artifact.artifact_id:
                        continue
                    if targeted_claim_ids and claim.claim_id not in targeted_claim_ids:
                        continue
                    if not targeted_claim_ids and summary_claim_ids and claim.claim_id not in summary_claim_ids:
                        continue
                    if evidence.evidence_id not in claim.evidence_ids:
                        claim.evidence_ids.append(evidence.evidence_id)
        run.missing_evidence = self.gate_evaluator.missing_evidence(run)
        if not run.missing_evidence and run.state == LifecycleState.EVIDENCE_REQUIRED:
            self._transition_run(run, LifecycleState.UNDER_REVIEW, actor_id, "evidence attached")
        self.store.save(run)
        return run

    def verify(self, run_id: str, reviewer_id: str) -> KernelRun:
        run = self.store.load(run_id)
        if run.state not in {LifecycleState.UNDER_REVIEW, LifecycleState.HANDOFF_PENDING}:
            raise TransitionError(f"Cannot verify from {run.state.value}.")
        self._enforce_material_action(run, reviewer_id, self._reviewer_roles(reviewer_id), "verify", run.project_id)
        for artifact in run.artifacts:
            if artifact.content_hash and artifact.content_hash != _content_hash(artifact.content):
                run.block_reason = "Artifact hash does not match current content."
                self._transition_run(run, LifecycleState.BLOCKED, reviewer_id, run.block_reason)
                self.store.save(run)
                raise TransitionError(run.block_reason)
            unsupported_claim = self._blocking_claim(run, artifact)
            if unsupported_claim:
                run.block_reason = f"Claim evidence status is not acceptable: {unsupported_claim}"
                self._transition_run(run, LifecycleState.BLOCKED, reviewer_id, run.block_reason)
                self.store.save(run)
                raise TransitionError(run.block_reason)
            if artifact.creator_id == reviewer_id:
                raise TransitionError("Artifact creator cannot verify own artifact.")
            artifact.verified_by = reviewer_id
            run.verification_records.append(
                VerificationRecord(
                    verification_id=_new_id("verification"),
                    artifact_id=artifact.artifact_id,
                    verifier_id=reviewer_id,
                    artifact_hash=artifact.content_hash,
                    result="approved",
                    timestamp=_now(),
                )
            )
        run.missing_evidence = self.gate_evaluator.missing_evidence(run)
        if run.missing_evidence:
            self._transition_run(run, LifecycleState.EVIDENCE_REQUIRED, reviewer_id, "verification missing evidence")
        else:
            self._transition_run(run, LifecycleState.APPROVED, reviewer_id, "independent verification approved")
        self.store.save(run)
        return run

    def record_human_approval(
        self,
        run_id: str,
        approver_id: str,
        decision: str,
        rationale: str,
        exact_action: str = "",
        constraints: list[str] | None = None,
        expires_at: str | None = None,
    ) -> KernelRun:
        run = self.store.load(run_id)
        if run.state != LifecycleState.AWAITING_HUMAN:
            raise TransitionError(f"Cannot record human approval from {run.state.value}.")
        if not approver_id.startswith("human-"):
            raise TransitionError("Human approval requires a stable human actor identifier.")
        if decision != "approved":
            self._transition_run(run, LifecycleState.REJECTED, approver_id, rationale)
        else:
            run.human_approval_by = approver_id
            run.approval_records.append(
                self.make_approval_record(
                    approver_id=approver_id,
                    decision=decision,
                    rationale=rationale,
                    exact_action=exact_action or ("release external" if run.request.external else "approve run"),
                    constraints=constraints,
                    expires_at=expires_at,
                )
            )
            self._transition_run(run, LifecycleState.APPROVED, approver_id, rationale)
        self.store.save(run)
        return run

    def fail_work(
        self,
        run_id: str,
        workstream_id: str,
        actor_id: str,
        error_type: str,
        error_message: str,
        retryable: bool,
    ) -> KernelRun:
        run = self.store.load(run_id)
        packet = self._packet(run, workstream_id)
        if packet.state not in {LifecycleState.DISPATCHED, LifecycleState.IN_PROGRESS}:
            raise TransitionError(f"Cannot fail work from {packet.state.value}.")
        packet.retries += 1
        can_retry = retryable and packet.retries <= packet.max_retries
        resolution = "retry_scheduled" if can_retry else "cancelled_downstream"
        run.failure_packets.append(
            FailurePacket(
                failure_id=_new_id("failure"),
                workstream_id=workstream_id,
                actor_id=actor_id,
                error_type=error_type,
                error_message=error_message,
                retryable=retryable,
                retry_count=packet.retries,
                resolution=resolution,
                timestamp=_now(),
            )
        )
        self._transition_run(run, LifecycleState.FAILED, actor_id, error_message)
        if can_retry:
            packet.state = LifecycleState.READY
            completed = {item.workstream_id for item in run.artifacts}
            run.runnable_packets = self.dependency_evaluator.runnable(run.packets, completed)
            self._transition_run(run, LifecycleState.READY, actor_id, "retry scheduled")
        else:
            packet.state = LifecycleState.FAILED
            for downstream in run.packets:
                if workstream_id in downstream.dependencies and downstream.artifact_id is None:
                    downstream.state = LifecycleState.CANCELLED
            self._transition_run(run, LifecycleState.CANCELLED, actor_id, "downstream work cancelled")
        self.store.save(run)
        return run

    def resume(self, run_id: str, actor_id: str) -> KernelRun:
        run = self.store.load(run_id)
        if run.state not in {LifecycleState.BLOCKED, LifecycleState.FAILED, LifecycleState.EVIDENCE_REQUIRED}:
            raise TransitionError(f"Cannot resume from {run.state.value}.")
        completed = {artifact.workstream_id for artifact in run.artifacts}
        run.runnable_packets = self.dependency_evaluator.runnable(run.packets, completed)
        next_state = LifecycleState.READY if run.runnable_packets else LifecycleState.HANDOFF_PENDING
        self._transition_run(run, next_state, actor_id, "run resumed")
        self.store.save(run)
        return run

    def authorize_release(self, run_id: str, actor_id: str) -> KernelRun:
        run = self.store.load(run_id)
        scoped_approvals = [
            record.approval_id
            for record in run.approval_records
            if record.approver_id == actor_id and record.exact_action in {"release external", "release external pitch", "external_send"}
        ]
        expired_scoped_approvals = [
            record
            for record in run.approval_records
            if record.approver_id == actor_id
            and record.exact_action in {"release external", "release external pitch", "external_send"}
            and record.expires_at
            and datetime.fromisoformat(record.expires_at) < datetime.now(timezone.utc)
        ]
        if expired_scoped_approvals:
            run.block_reason = "Release approval is expired."
            self.store.save(run)
            raise TransitionError(run.block_reason)
        stale_hash_approval = self._stale_release_hash_approval(run, actor_id)
        if stale_hash_approval:
            run.block_reason = "Release approval artifact hash does not match current artifact hash."
            self.store.save(run)
            raise TransitionError(run.block_reason)
        if run.risk_level in {RiskLevel.HIGH, RiskLevel.CRITICAL} and not scoped_approvals:
            run.block_reason = "Release requires approval scoped to release external action."
            self.store.save(run)
            raise TransitionError(run.block_reason)
        decision = self.gate_evaluator.release_decision(run, actor_id)
        if decision != GateDecision.PERMIT:
            raise TransitionError("Release is not authorized without required human approval.")
        self._transition_run(run, LifecycleState.RELEASE_READY, actor_id, "release authorized")
        self.store.save(run)
        return run

    def _stale_release_hash_approval(self, run: KernelRun, actor_id: str) -> bool:
        current_hashes = {artifact.content_hash for artifact in run.artifacts if artifact.content_hash}
        if not current_hashes:
            return False
        scoped_records = [
            record
            for record in run.approval_records
            if record.approver_id == actor_id
            and record.exact_action in {"release external", "release external pitch", "external_send"}
            and record.approved_artifact_hash
        ]
        return any(record.approved_artifact_hash not in current_hashes for record in scoped_records)

    def _enforce_material_action(
        self,
        run: KernelRun,
        actor_id: str,
        actor_roles: list[str],
        action: str,
        resource: str,
    ) -> None:
        decision = self.policy_registry.evaluate(
            actor_id=actor_id,
            actor_roles=actor_roles,
            action=action,
            resource=resource,
            risk_level=run.risk_level.value,
            evidence_ids=[item.evidence_id for item in run.evidence],
            approval_ids=[record.approval_id for record in run.approval_records],
        )
        self._record_policy_decision(run, decision)
        if decision.outcome == PolicyOutcome.PERMIT:
            return
        run.block_reason = decision.reason
        target_state = LifecycleState.AWAITING_HUMAN if decision.outcome == PolicyOutcome.HOLD else LifecycleState.BLOCKED
        self._transition_run(run, target_state, actor_id, decision.reason)
        self.store.save(run)
        raise TransitionError(decision.reason)

    def _record_policy_decision(self, run: KernelRun, decision) -> None:
        run.policy_decisions.append(
            PolicyDecisionRecord(
                decision_id=decision.decision_id,
                policy_version=decision.policy_version,
                actor_id=decision.actor_id,
                requested_action=decision.requested_action,
                resource=decision.resource,
                risk_level=decision.risk_level,
                outcome=decision.outcome.value,
                applicable_rules=decision.applicable_rules,
                required_conditions=decision.required_conditions,
                missing_evidence=decision.missing_evidence,
                required_approval=decision.required_approval,
                reason=decision.reason,
                timestamp=decision.timestamp,
            )
        )

    def replay(self, run_id: str) -> list[RuntimeEvent]:
        return self.store.events(run_id)

    def status_report(self, run_id: str) -> str:
        run = self.store.load(run_id)
        return (
            f"Run {run.run_id} state={run.state.value} risk={run.risk_level.value} "
            f"packets={len(run.packets)} artifacts={len(run.artifacts)} "
            f"missing_evidence={','.join(run.missing_evidence) or 'none'} "
            f"execution_mode={run.execution_mode}"
        )

    def _packet(self, run: KernelRun, workstream_id: str) -> WorkPacket:
        for packet in run.packets:
            if packet.workstream_id == workstream_id:
                return packet
        raise KeyError(workstream_id)

    def _transition_run(self, run: KernelRun, to_state: LifecycleState, actor_id: str, reason: str) -> None:
        allowed = LEGAL_TRANSITIONS.get(run.state, set())
        if to_state not in allowed:
            raise TransitionError(f"Illegal transition {run.state.value} -> {to_state.value}.")
        from_state = run.state
        run.state = to_state
        self._record(run, from_state, to_state, actor_id, reason)

    def _record(
        self,
        run: KernelRun,
        from_state: LifecycleState | None,
        to_state: LifecycleState,
        actor_id: str,
        reason: str,
    ) -> None:
        self.store.append_event(
            RuntimeEvent(
                event_id=_new_id("event"),
                run_id=run.run_id,
                from_state=from_state,
                to_state=to_state,
                actor_id=actor_id,
                reason=reason,
                timestamp=_now(),
            )
        )
