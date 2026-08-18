"""Typed AgencyOS runtime schemas.

Priority 2 slice: machine-readable contracts for core runtime records.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


SCHEMA_VERSION = "agencyos.runtime.v1"
SUPPORTED_OLD_SCHEMA_VERSIONS = {"agencyos.runtime.v0"}


class SchemaMigrationError(ValueError):
    """Raised when a runtime record cannot be migrated."""


def _now() -> datetime:
    return datetime.now(timezone.utc)


class RuntimeStatus(str, Enum):
    RECEIVED = "received"
    INTAKE_REQUIRED = "intake_required"
    CLASSIFIED = "classified"
    PLANNED = "planned"
    READY = "ready"
    RUNNING = "running"
    BLOCKED = "blocked"
    HOLD = "hold"
    ESCALATED = "escalated"
    AWAITING_HUMAN = "awaiting_human"
    UNDER_REVIEW = "under_review"
    EVIDENCE_CHECK = "evidence_check"
    VERIFIED = "verified"
    APPROVED = "approved"
    REJECTED = "rejected"
    RELEASED = "released"
    CLOSED = "closed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ScopeClassification(str, Enum):
    ONE_TASK = "one_task"
    ONE_PROJECT = "one_project"
    MULTIPLE_PROJECTS = "multiple_projects"
    ONGOING_OPERATING_SYSTEM = "ongoing_operating_system"


class ActorKind(str, Enum):
    HUMAN = "human"
    BEING = "being"
    RUNTIME = "runtime"
    AGENCY = "agency"
    SPECIALIST = "specialist"
    TOOL = "tool"


class EvidenceStatus(str, Enum):
    VERIFIED = "verified"
    SUPPORTED = "supported"
    INFERRED = "inferred"
    ASSUMED = "assumed"
    UNKNOWN = "unknown"
    UNSUPPORTED = "unsupported"


class PolicyOutcome(str, Enum):
    PERMIT = "permit"
    WARN = "warn"
    HOLD = "hold"
    BLOCK = "block"
    ESCALATE = "escalate"


LEGAL_TRANSITIONS: dict[RuntimeStatus, set[RuntimeStatus]] = {
    RuntimeStatus.RECEIVED: {RuntimeStatus.INTAKE_REQUIRED, RuntimeStatus.CLASSIFIED, RuntimeStatus.BLOCKED},
    RuntimeStatus.INTAKE_REQUIRED: {RuntimeStatus.CLASSIFIED, RuntimeStatus.BLOCKED, RuntimeStatus.CANCELLED},
    RuntimeStatus.CLASSIFIED: {RuntimeStatus.PLANNED, RuntimeStatus.HOLD, RuntimeStatus.AWAITING_HUMAN, RuntimeStatus.BLOCKED},
    RuntimeStatus.PLANNED: {RuntimeStatus.READY, RuntimeStatus.HOLD, RuntimeStatus.BLOCKED},
    RuntimeStatus.READY: {RuntimeStatus.RUNNING, RuntimeStatus.HOLD, RuntimeStatus.CANCELLED},
    RuntimeStatus.RUNNING: {RuntimeStatus.UNDER_REVIEW, RuntimeStatus.EVIDENCE_CHECK, RuntimeStatus.FAILED, RuntimeStatus.BLOCKED},
    RuntimeStatus.HOLD: {RuntimeStatus.READY, RuntimeStatus.AWAITING_HUMAN, RuntimeStatus.BLOCKED, RuntimeStatus.CANCELLED},
    RuntimeStatus.ESCALATED: {RuntimeStatus.AWAITING_HUMAN, RuntimeStatus.BLOCKED, RuntimeStatus.CANCELLED},
    RuntimeStatus.AWAITING_HUMAN: {RuntimeStatus.APPROVED, RuntimeStatus.REJECTED, RuntimeStatus.CANCELLED},
    RuntimeStatus.UNDER_REVIEW: {RuntimeStatus.EVIDENCE_CHECK, RuntimeStatus.VERIFIED, RuntimeStatus.REJECTED},
    RuntimeStatus.EVIDENCE_CHECK: {RuntimeStatus.VERIFIED, RuntimeStatus.BLOCKED, RuntimeStatus.HOLD},
    RuntimeStatus.VERIFIED: {RuntimeStatus.APPROVED, RuntimeStatus.REJECTED},
    RuntimeStatus.APPROVED: {RuntimeStatus.RELEASED, RuntimeStatus.CLOSED},
    RuntimeStatus.REJECTED: {RuntimeStatus.CANCELLED, RuntimeStatus.BLOCKED},
    RuntimeStatus.BLOCKED: {RuntimeStatus.READY, RuntimeStatus.CANCELLED},
    RuntimeStatus.FAILED: {RuntimeStatus.READY, RuntimeStatus.CANCELLED},
    RuntimeStatus.RELEASED: {RuntimeStatus.CLOSED},
    RuntimeStatus.CANCELLED: set(),
    RuntimeStatus.CLOSED: set(),
}


def validate_transition(previous: RuntimeStatus, new: RuntimeStatus) -> None:
    if new not in LEGAL_TRANSITIONS.get(previous, set()):
        raise ValueError(f"Illegal transition {previous.value} -> {new.value}.")


class RuntimeModel(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    id: str
    schema_version: str = SCHEMA_VERSION
    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)
    actor_id: str
    status: RuntimeStatus = RuntimeStatus.RECEIVED
    provenance: str = "local_runtime"

    @field_validator("schema_version")
    @classmethod
    def schema_version_must_be_current(cls, value: str) -> str:
        if value != SCHEMA_VERSION:
            raise ValueError(f"Unsupported schema_version {value}.")
        return value

    @field_validator("id", "actor_id")
    @classmethod
    def identifiers_are_stable(cls, value: str) -> str:
        if not value or " " in value:
            raise ValueError("Stable identifiers must be non-empty and contain no spaces.")
        if value[0].isupper():
            raise ValueError("Display names cannot be used as stable identifiers.")
        return value


class KernelRunSnapshot(BaseModel):
    model_config = ConfigDict(extra="allow")

    schema_version: Literal["kernel.p1.v1"]
    run_id: str
    request: dict[str, Any]
    project_id: str
    state: str
    risk_level: str
    execution_mode: str


class Actor(RuntimeModel):
    display_name: str
    kind: ActorKind
    roles: list[str] = Field(default_factory=list)
    personality_id: str | None = None
    behavioral_posture_id: str | None = None
    capability_ids: list[str] = Field(default_factory=list)
    permission_ids: list[str] = Field(default_factory=list)


class Being(RuntimeModel):
    display_name: str
    runtime_actor_id: str
    role_ids: list[str] = Field(default_factory=list)
    capability_ids: list[str] = Field(default_factory=list)
    permission_ids: list[str] = Field(default_factory=list)
    personality_id: str | None = None
    behavioral_posture_id: str | None = None

    @model_validator(mode="after")
    def personality_does_not_grant_permission(self) -> "Being":
        if self.personality_id and not self.permission_ids:
            return self
        return self


class Capability(RuntimeModel):
    name: str
    description: str = ""


class Permission(RuntimeModel):
    action: str
    resource: str
    constraints: list[str] = Field(default_factory=list)


class ToolGrant(RuntimeModel):
    tool_name: str
    allowed_actions: list[str]
    denied_actions: list[str] = Field(default_factory=list)


class Agency(RuntimeModel):
    name: str
    member_actor_ids: list[str] = Field(default_factory=list)
    capability_ids: list[str] = Field(default_factory=list)


class Request(RuntimeModel):
    human_owner_id: str
    desired_outcome: str
    scope: ScopeClassification | None = None
    constraints: list[str] = Field(default_factory=list)
    source_inputs: list[str] = Field(default_factory=list)
    allowed_tools: list[str] = Field(default_factory=list)
    off_limits_actions: list[str] = Field(default_factory=list)
    approval_requirements: list[str] = Field(default_factory=list)
    definition_of_done: list[str] = Field(default_factory=list)
    installation_mode: str = "local_first"
    existing_project_id: str | None = None
    requested_actor_ids: list[str] = Field(default_factory=list)
    sensitivity_classification: RiskLevel = RiskLevel.LOW


class Project(RuntimeModel):
    name: str
    human_owner_id: str | None = None
    source_path: str | None = None


class Workstream(RuntimeModel):
    project_id: str
    name: str
    owner_actor_id: str
    dependencies: list[str] = Field(default_factory=list)
    definition_of_done: list[str]
    risk_level: RiskLevel = RiskLevel.LOW


class WorkItem(RuntimeModel):
    project_id: str
    workstream_id: str
    task: str
    assigned_actor_id: str
    expected_output: str = ""
    inputs: list[str] = Field(default_factory=list)
    source_of_truth_refs: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    allowed_tools: list[str] = Field(default_factory=list)
    data_boundary: str = "internal"
    risk_level: RiskLevel
    required_evidence: list[str] = Field(default_factory=list)
    definition_of_done: list[str]
    human_gate: str | None = None
    pause_condition: str | None = None
    retry_policy: str = "no_retry"
    timeout_policy: str = "no_timeout"
    destination_after_completion: str = "handoff"


class Dependency(RuntimeModel):
    project_id: str
    upstream_work_item_id: str
    downstream_work_item_id: str
    dependency_type: str = "requires_completion"
    condition: str | None = None


class WorkPacket(RuntimeModel):
    project_id: str
    workstream_id: str
    work_item_id: str
    assigned_actor_id: str
    task: str
    expected_output: str = "local artifact"
    inputs: list[str] = Field(default_factory=list)
    source_of_truth_refs: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    allowed_tools: list[str] = Field(default_factory=list)
    data_boundary: str = "internal"
    risk_level: RiskLevel
    required_evidence: list[str] = Field(default_factory=list)
    definition_of_done: list[str]
    human_gate: str | None = None
    pause_condition: str | None = None
    retry_policy: str = "no_retry"
    timeout_policy: str = "no_timeout"
    destination_after_completion: str = "handoff"


class Policy(RuntimeModel):
    name: str
    version: str
    rules: list[str] = Field(default_factory=list)


class PolicyDecision(RuntimeModel):
    policy_id: str
    outcome: PolicyOutcome
    requested_action: str
    resource: str
    risk_level: RiskLevel
    applicable_rules: list[str] = Field(default_factory=list)
    required_conditions: list[str] = Field(default_factory=list)
    missing_evidence: list[str] = Field(default_factory=list)
    required_approval: str | None = None
    reason: str


class Artifact(RuntimeModel):
    project_id: str
    workstream_id: str
    path: str
    content_hash: str
    creator_actor_id: str | None = None
    claim_ids: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)
    release_status: RuntimeStatus = RuntimeStatus.HOLD


class ArtifactVersion(RuntimeModel):
    artifact_id: str
    content_hash: str
    version_number: int = Field(ge=1)
    artifact_path: str | None = None
    creator_actor_id: str | None = None
    work_item_id: str | None = None


class Claim(RuntimeModel):
    artifact_id: str
    text: str
    claim_type: str = "general"
    evidence_ids: list[str] = Field(default_factory=list)
    evidence_status: EvidenceStatus = EvidenceStatus.UNKNOWN
    required_approval: str | None = None


class EvidenceItem(RuntimeModel):
    project_id: str
    workstream_id: str
    summary: str
    source_ref: str | None = None
    evidence_status: EvidenceStatus = EvidenceStatus.UNKNOWN
    sensitive: bool = False


class Verification(RuntimeModel):
    artifact_id: str
    verifier_actor_id: str
    result: str
    evidence_ids: list[str] = Field(default_factory=list)
    artifact_hash: str | None = None


class Approval(RuntimeModel):
    approver_id: str
    exact_action: str
    decision: Literal["approve", "reject", "revise", "defer"]
    scope: str
    constraints: list[str] = Field(default_factory=list)
    expires_at: datetime | None = None
    approved_artifact_hash: str | None = None

    @field_validator("approver_id")
    @classmethod
    def approver_must_be_human_id(cls, value: str) -> str:
        if not value.startswith("human-"):
            raise ValueError("Approval requires a stable human approver identifier.")
        return value


class ApprovalRequest(RuntimeModel):
    requested_action: str
    resource_id: str
    required_approver_id: str
    reason: str
    project_id: str | None = None
    work_item_id: str | None = None
    artifact_hash: str | None = None
    constraints: list[str] = Field(default_factory=list)
    expires_at: datetime | None = None

    @field_validator("required_approver_id")
    @classmethod
    def required_approver_must_be_human_id(cls, value: str) -> str:
        if not value.startswith("human-"):
            raise ValueError("Approval request requires a stable human approver identifier.")
        return value


class ApprovalDecision(RuntimeModel):
    approval_request_id: str
    approver_id: str
    exact_action: str
    decision: Literal["approve", "reject", "revise", "defer"]
    scope: str
    constraints: list[str] = Field(default_factory=list)
    approved_artifact_hash: str | None = None

    @field_validator("approver_id")
    @classmethod
    def decision_approver_must_be_human_id(cls, value: str) -> str:
        if not value.startswith("human-"):
            raise ValueError("Approval decision requires a stable human approver identifier.")
        return value


class Handoff(RuntimeModel):
    project_id: str
    workstream_id: str | None = None
    artifact_ids: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)
    destination: str = "review"


class RuntimeEvent(RuntimeModel):
    correlation_id: str
    project_id: str
    workstream_id: str | None = None
    work_item_id: str | None = None
    actor_role: str = "runtime"
    previous_state: RuntimeStatus | None = None
    new_state: RuntimeStatus
    trigger: str
    reason: str = ""
    input_refs: list[str] = Field(default_factory=list)
    artifact_refs: list[str] = Field(default_factory=list)
    evidence_refs: list[str] = Field(default_factory=list)
    policy_decision_id: str | None = None
    approval_id: str | None = None
    runtime_version: str = SCHEMA_VERSION


class FailurePacket(RuntimeModel):
    failed_component: str
    failed_work_item_id: str | None = None
    error_type: str
    error_message: str
    inputs_used: list[str] = Field(default_factory=list)
    state_at_failure: RuntimeStatus
    completed_outputs: list[str] = Field(default_factory=list)
    affected_dependencies: list[str] = Field(default_factory=list)
    safe_retry_status: str
    recovery_options: list[str] = Field(default_factory=list)
    human_input_required: bool = False
    evidence_preserved: list[str] = Field(default_factory=list)


class ReconciliationPacket(RuntimeModel):
    project_id: str
    conflicting_artifact_ids: list[str] = Field(default_factory=list)
    conflicting_propositions: list[str] = Field(default_factory=list)
    resolution: str | None = None
    rationale: str | None = None


class DecisionPacket(RuntimeModel):
    project_id: str
    decision_needed: str
    options: list[str]
    recommended_option: str | None = None
    required_approver_id: str | None = None


class CloseoutPacket(RuntimeModel):
    project_id: str
    artifact_ids: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)
    approval_ids: list[str] = Field(default_factory=list)
    verification_ids: list[str] = Field(default_factory=list)


class LearningProposal(RuntimeModel):
    project_id: str
    proposed_learning: str
    evidence_ids: list[str] = Field(default_factory=list)
    approval_id: str | None = None


class Registry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    projects: list[Project] = Field(default_factory=list)
    requests: list[Request] = Field(default_factory=list)
    workstreams: list[Workstream] = Field(default_factory=list)
    work_items: list[WorkItem] = Field(default_factory=list)
    dependencies: list[Dependency] = Field(default_factory=list)
    work_packets: list[WorkPacket] = Field(default_factory=list)
    actors: list[Actor] = Field(default_factory=list)
    beings: list[Being] = Field(default_factory=list)
    agencies: list[Agency] = Field(default_factory=list)
    capabilities: list[Capability] = Field(default_factory=list)
    permissions: list[Permission] = Field(default_factory=list)
    tool_grants: list[ToolGrant] = Field(default_factory=list)
    policies: list[Policy] = Field(default_factory=list)
    artifacts: list[Artifact] = Field(default_factory=list)
    artifact_versions: list[ArtifactVersion] = Field(default_factory=list)
    claims: list[Claim] = Field(default_factory=list)
    evidence: list[EvidenceItem] = Field(default_factory=list)
    verifications: list[Verification] = Field(default_factory=list)
    approvals: list[Approval] = Field(default_factory=list)
    approval_requests: list[ApprovalRequest] = Field(default_factory=list)
    approval_decisions: list[ApprovalDecision] = Field(default_factory=list)
    handoffs: list[Handoff] = Field(default_factory=list)
    events: list[RuntimeEvent] = Field(default_factory=list)
    failures: list[FailurePacket] = Field(default_factory=list)
    reconciliations: list[ReconciliationPacket] = Field(default_factory=list)
    decisions: list[DecisionPacket] = Field(default_factory=list)
    closeouts: list[CloseoutPacket] = Field(default_factory=list)
    learning: list[LearningProposal] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_unique_ids_and_references(self) -> "Registry":
        records = []
        for collection in (
            self.projects,
            self.requests,
            self.workstreams,
            self.work_items,
            self.dependencies,
            self.work_packets,
            self.actors,
            self.beings,
            self.agencies,
            self.capabilities,
            self.permissions,
            self.tool_grants,
            self.policies,
            self.artifacts,
            self.artifact_versions,
            self.claims,
            self.evidence,
            self.verifications,
            self.approvals,
            self.approval_requests,
            self.approval_decisions,
            self.handoffs,
            self.events,
            self.failures,
            self.reconciliations,
            self.decisions,
            self.closeouts,
            self.learning,
        ):
            records.extend(collection)
        ids = [record.id for record in records]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate stable identifiers are not allowed.")

        project_ids = {project.id for project in self.projects}
        workstream_ids = {workstream.id for workstream in self.workstreams}

        for workstream in self.workstreams:
            if workstream.project_id not in project_ids:
                raise ValueError(f"Broken project reference {workstream.project_id}.")

        for work_item in self.work_items:
            if work_item.project_id not in project_ids:
                raise ValueError(f"Broken project reference {work_item.project_id}.")
            if work_item.workstream_id not in workstream_ids:
                raise ValueError(f"Broken workstream reference {work_item.workstream_id}.")

        return self


def migrate_record(record: dict) -> dict:
    version = record.get("schema_version")
    if version == SCHEMA_VERSION:
        return record
    if version in SUPPORTED_OLD_SCHEMA_VERSIONS:
        migrated = dict(record)
        migrated["schema_version"] = SCHEMA_VERSION
        return migrated
    raise SchemaMigrationError(f"Unsupported schema_version {version}.")


SCHEMA_CATALOG_MODELS = [
    Request,
    Project,
    Workstream,
    WorkItem,
    Being,
    Actor,
    Agency,
    Capability,
    Permission,
    ToolGrant,
    Dependency,
    WorkPacket,
    Policy,
    PolicyDecision,
    Handoff,
    Artifact,
    ArtifactVersion,
    Claim,
    EvidenceItem,
    Verification,
    Approval,
    ApprovalRequest,
    ApprovalDecision,
    RuntimeEvent,
    FailurePacket,
    ReconciliationPacket,
    DecisionPacket,
    CloseoutPacket,
    LearningProposal,
    KernelRunSnapshot,
    Registry,
]


def schema_catalog() -> dict[str, dict]:
    return {model.__name__: model.model_json_schema() for model in SCHEMA_CATALOG_MODELS}
