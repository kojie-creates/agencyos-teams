# Runtime Kernel Status

Status:

```text
Priority 1 executable slice implemented.
Priority 2 complete for current repo shape.
Priority 2 durable storage slice implemented.
Priority 3 canonical policy registry first slice implemented.
Priority 3 dispatch policy wiring first slice implemented.
Priority 4 proof/export hardening implemented.
Priority 1 completion tests pass.
Autonomous operations remain bounded by human gates.
```

## Implemented

```text
Deterministic enforcement kernel.
Local durable JSON and JSONL state store.
SQLite runtime mirror for queryable run and event history.
SQLite-first runtime load and event replay.
Append-only runtime event replay from the runtime perspective.
Lifecycle state enforcement with explicit legal transitions.
Plain-language intake-required route.
Project resolution from explicit project, first-run context, or authorized creation.
Scope/risk classification for low, medium, high, and critical risk labels.
Dependency cycle detection.
Runnable work packet planning.
Registry-based default Being assignment.
Packet permissions, withheld actions, expected outputs, required evidence, and pause conditions.
Deterministic batch planning mode.
Dependency-safe execution batch metadata.
Retryable failure packet handling.
Downstream cancellation for exhausted failed dependencies.
Handoff creation.
Claim-preserving reconciliation records.
Evidence-required closeout block.
Evidence attachment.
Independent verification guard.
Human approval gate for high-risk work.
Structured human approval records.
Release authorization block without matching human approval.
Closeout records.
Learning records.
Operator-readable status report.
JSON CLI entry point.
SQLite-backed CLI run history listing.
Pydantic runtime schema inventory.
JSON Schema catalog for runtime contracts.
Markdown project-packet importer for existing project folders.
Executable policy registry with default-deny behavior.
Human-readable runtime policy view backed by executable JSON.
Dispatch checks policy before material work starts.
Release checks exact-action approval scope.
Closeout checks policy before closing.
Evidence attachment checks policy before evidence is accepted.
Sensitive evidence holds for human approval.
Verification checks policy before review approval.
Memory-write attempts are explicitly blocked.
Governance-policy modification attempts are explicitly blocked.
Destructive-action attempts are explicitly blocked without exact target authorization.
Policy decisions are persisted on the run record.
Policy decisions are mirrored into SQLite and queryable by CLI.
Claim records are mirrored into SQLite and queryable by CLI.
Expired release approvals are rejected.
Release approvals tied to stale artifact hashes are rejected.
Verification rejects artifacts whose current content no longer matches the recorded artifact hash.
Verification records preserve reviewed artifact hash and verifier.
Claim-level evidence lock blocks claims with unacceptable evidence status.
Kernel claim strings are promoted into first-class claim records linked to artifact IDs.
Verification uses first-class claim records when present and preserves legacy reconciliation claims.
Evidence attachment links supporting evidence IDs to matching claim records.
Evidence attachment can target specific claim records when claim IDs are supplied.
Evidence summary text can auto-link evidence to exact matching claim text.
Reconciliation detects conflicting evidence statuses for matching claim text.
Tool-use attempts require explicit permission.
Sensitive data is blocked from public-boundary actions.
Schema-version validation.
Runtime transition validation helper.
Registry validation for duplicate IDs and broken project/workstream references.
Old schema migration stub for agencyos.runtime.v0 to agencyos.runtime.v1.
CLI request loading now passes through schema validation before kernel start.
SQLite runtime payload loading now passes through Pydantic boundary validation before dataclass decode.
Portable run proof bundle export.
Local filesystem artifact adapter.
Local artifact writes are constrained to `.agencyos-runtime/artifacts/{run_id}`.
Governed model draft adapter for local artifact generation.
Model draft adapter blocks sensitive or external runs.
OpenAI Responses model adapter shell behind local credential/config policy.
OpenAI provider is disabled unless `.agencyos-runtime/config.local.json` enables it and the configured API-key environment variable exists.
Safe OpenAI config example is provided at `.agencyos-runtime/config.local.example.json`.
Vendor-agnostic OpenAI-compatible local provider supports LM Studio-style localhost endpoints.
Model draft calls create durable model-call audit records.
Model adapter and model-policy failures create durable failure packets before returning an error.
Export bundle manifest with artifact hashes, section counts, and bundle hash.
Export bundle verification command.
Export verification checks manifest counts and recomputes artifact content hashes.
Export manifest counts cover model-call, failure, closeout, and learning records.
Export verification checks export and manifest schema versions.
Export verification checks required bundle sections are present.
Export verification reports failed checks for human review.
Export verification checks runtime event-chain continuity.
Export verification checks final event state against exported run state.
Export verification checks internal ID references for artifacts, claims, evidence, approvals, model-call records, closeout records, and events.
Export verification checks duplicate or missing IDs across exported record sections.
```

## Runtime Entry Points

```text
python -m agencyos run --request request.json
python -m agencyos intake --text "..." --actor-id actor-operator --human-owner-id human-kojie
python -m agencyos status --run-id RUN_ID
python -m agencyos events --run-id RUN_ID
python -m agencyos runs
python -m agencyos policy-decisions --run-id RUN_ID
python -m agencyos claim-records --run-id RUN_ID
python -m agencyos model-calls --run-id RUN_ID
python -m agencyos failure-packets --run-id RUN_ID
python -m agencyos export-run --run-id RUN_ID --output exports/run-export.json
python -m agencyos verify-export --input exports/run-export.json
python -m agencyos import-project --project projects/diana-spend-reporting-assistant --output registry.json
python -m agencyos dispatch --run-id RUN_ID
python -m agencyos complete --run-id RUN_ID --workstream-id research --path research.md --content "..." --actor-id actor-research
python -m agencyos model-draft --run-id RUN_ID --workstream-id research --path drafts/research.md --prompt "..." --model gpt-local-draft --actor-id actor-research
python -m agencyos model-draft --run-id RUN_ID --workstream-id research --path drafts/research.md --prompt "..." --model active --provider openai_compatible_local --actor-id actor-research
python -m agencyos model-draft --run-id RUN_ID --workstream-id research --path drafts/research.md --prompt "..." --model gpt-5.6-luna --provider openai --actor-id actor-research
python -m agencyos handoff --run-id RUN_ID --actor-id actor-operator
python -m agencyos evidence --run-id RUN_ID --workstream-id build --path evidence/build-proof.txt --summary "..." --actor-id actor-evidence
python -m agencyos evidence --run-id RUN_ID --workstream-id build --path evidence/build-proof.txt --summary "..." --actor-id actor-evidence --claim-id CLAIM_ID
python -m agencyos verify --run-id RUN_ID --reviewer-id actor-verifier
python -m agencyos approve --run-id RUN_ID --approver-id human-kojie --decision approved --rationale "..."
python -m agencyos reject --run-id RUN_ID --approver-id human-kojie --rationale "..."
python -m agencyos release --run-id RUN_ID --actor-id human-kojie
python -m agencyos fail --run-id RUN_ID --workstream-id research --actor-id being-atlas --error-type tool_error --error-message "..." --retryable
python -m agencyos resume --run-id RUN_ID --actor-id actor-operator
python -m agencyos close --run-id RUN_ID --actor-id actor-operator
```

Each command accepts:

```text
--root PATH
```

## Current State Model

```text
intake_required
received
classified
planned
awaiting_dependencies
ready
dispatched
in_progress
handoff_pending
under_review
evidence_required
awaiting_human
approved
rejected
blocked
failed
cancelled
release_ready
released
closeout_pending
closed
```

## Persistence Design

```text
.agencyos-runtime/runs/{run_id}.json
.agencyos-runtime/runs/{run_id}.events.jsonl
.agencyos-runtime/runtime.sqlite3
```

Runtime state is local-first. JSON/JSONL remains readable source material, and SQLite mirrors run/event history for queryable runtime visibility.

## Markdown Project Import

Implemented in:

```text
agencyos/project_importer.py
```

The importer reads the existing project packet files without replacing them:

```text
project-brief.md
plan.md
assigned-beings.md
assigned-agencies.md
governance-notes.md
handoffs.md
```

It emits a typed `Registry` containing project, request, workstream, Being, agency, policy, and handoff records.
It also imports evidence files, deliverable artifacts with SHA-256 hashes, closeout packets, and learning proposals.
Workstream README files import into typed `WorkItem` records with inputs, expected outputs, definitions of done, and pause conditions.
Deliverable `Evidence Status` tables import into typed `Claim` records.

## Schema Inventory

Implemented in:

```text
agencyos/schemas.py
```

Current typed schemas:

```text
Request
Project
Workstream
WorkItem
Being
Dependency
WorkPacket
Actor
Agency
Capability
Permission
ToolGrant
Policy
PolicyDecision
Handoff
Artifact
ArtifactVersion
Claim
EvidenceItem
Verification
Approval
ApprovalRequest
ApprovalDecision
RuntimeEvent
FailurePacket
ReconciliationPacket
DecisionPacket
CloseoutPacket
LearningProposal
Registry
```

Controlled vocabularies:

```text
RuntimeStatus
RiskLevel
ScopeClassification
ActorKind
EvidenceStatus
PolicyOutcome
```

Validation currently rejects:

```text
Unknown statuses.
Unsupported schema versions.
Malformed request records at CLI boundary.
Missing assigned actor authority on work items.
Duplicate stable identifiers in registries.
Broken project/workstream references.
Display names used as stable identifiers.
Invalid state transitions through validate_transition.
Non-human approval identifiers.
```

## Policy Inventory

```text
Low-risk internal reversible work may plan and become ready.
External-only work is medium risk.
Sensitive or irreversible work is high risk.
High-risk external sensitive irreversible work pauses at awaiting_human.
Release requires matching human approval.
Closeout requires complete handoff and required evidence.
Verifier cannot be the artifact creator.
Illegal transitions are rejected.
Dependency cycles are blocked.
Retry exhaustion cancels downstream dependent work.
Conflicting claims are preserved and marked for human decision.
Conflicting first-class claim evidence statuses are preserved and marked for human decision.
Canonical policy registry exists for initial internal artifact and external-action gates.
```

Medium-risk means work that can affect outside perception, workflow, cost, or decisions, but does not directly execute an irreversible, sensitive, legal, financial, or public action.

Examples:

```text
Client-facing drafts before sending.
External proposal preparation.
Non-sensitive business summaries.
Workflow recommendations.
Internal strategy artifacts that may later become external.
Local or vendor model use on non-sensitive internal content.
Outputs that require review before use.
```

Not medium-risk:

```text
Purely local reversible drafts with no sensitive data are low-risk.
Public sends, legal or financial advice, sensitive data, and irreversible actions are high-risk.
```

## Demonstration Instructions

Create `request.json`:

```json
{
  "request_id": "demo-internal",
  "title": "Create internal local artifacts",
  "actor_id": "actor-operator",
  "requested_outcome": "Create internal reversible outputs.",
  "action_class": "internal_artifact",
  "reversible": true,
  "external": false,
  "sensitive": false,
  "required_workstreams": ["research", "build"]
}
```

Run:

```text
python -m agencyos run --request request.json
python -m agencyos dispatch --run-id RUN_ID
python -m agencyos complete --run-id RUN_ID --workstream-id research --path research.md --content "Research output" --actor-id actor-research
python -m agencyos complete --run-id RUN_ID --workstream-id build --path build.md --content "Build output" --actor-id actor-build
python -m agencyos handoff --run-id RUN_ID --actor-id actor-operator
python -m agencyos status --run-id RUN_ID
python -m agencyos events --run-id RUN_ID
```

High-risk hold demo:

```json
{
  "request_id": "demo-high-risk",
  "title": "Send external pitch",
  "actor_id": "actor-operator",
  "requested_outcome": "Send an external pitch.",
  "action_class": "external_send",
  "reversible": false,
  "external": true,
  "sensitive": true,
  "required_workstreams": ["pitch"]
}
```

Run:

```text
python -m agencyos run --request request.json
python -m agencyos approve --run-id RUN_ID --approver-id human-kojie --decision approved --rationale "Approved sanitized demo."
```

## Tested

```text
Internal reversible request blocks closeout until evidence, then verifies and closes.
High-risk external request pauses at human gate and cannot release without human approval.
Illegal transitions are rejected.
Dependency cycles block planning.
CLI run, status, events, and approve commands return JSON.
Non-human approval fails.
Policy registry blocks unknown actors and unknown actions.
Policy registry holds external sends without human approval.
Kernel dispatch blocks unknown packet actions before execution.
Kernel dispatch holds external-send actions before execution without approval.
Release rejects approvals not scoped to external release.
Closeout blocks when no closeout policy permits the action.
Sensitive evidence attachment holds before persistence without approval.
Verification blocks when no independent-review policy permits the action.
Adversarial policy tests cover memory write, governance policy change, and destructive action blocks.
Blocked dispatch persists the policy decision record.
CLI policy-decisions lists SQLite-backed policy history.
CLI claim-records lists SQLite-backed claim history.
CLI export-run writes a portable proof bundle.
Exported proof bundles include a manifest hash and artifact hash index.
CLI verify-export validates bundle hash and artifact hash index.
CLI verify-export rejects forged manifest counts and artifact content hash mismatches.
CLI verify-export rejects unsupported export schema versions.
CLI verify-export rejects missing required export sections.
CLI verify-export reports failed checks for schema, bundle hash, artifact hashes, counts, and artifact content hashes.
CLI verify-export rejects forged event-chain transitions.
CLI verify-export rejects mismatched final event and run state.
CLI verify-export rejects broken internal bundle references.
CLI verify-export rejects duplicate or missing record IDs.
Expired release approval cannot authorize release.
Release approval for stale artifact hash cannot authorize release.
Tampered artifact content cannot pass verification after hash capture.
Verification records include reviewed artifact hash.
Unknown or unsupported required claim status blocks verification.
Supported or verified claim status may pass verification.
Completed artifacts create first-class claim records for proof-layer validation.
Claim records are queryable from SQLite.
Evidence attachment links claim records to supporting evidence IDs.
Evidence attachment can link evidence to selected claim records through CLI.
Evidence summary exact-phrase matching narrows claim links when possible.
Reconciliation flags conflicting first-class claim evidence statuses.
Denied tool-use attempts are blocked before dispatch.
Sensitive requests cannot write public artifacts.
Checked-in runtime policy JSON loads and permits low-risk internal artifact work.
Valid runtime schema set loads.
Priority 2 spec schema names instantiate.
Priority 2 schemas export through JSON Schema catalog.
Existing markdown project packet imports into a typed Registry.
CLI import-project writes Registry JSON.
Evidence, deliverables, closeout, and learning import into typed records.
Workstream README files import into typed work items.
Deliverable evidence-status tables import into typed claims.
Missing required authority is rejected.
Unknown statuses are rejected.
Invalid transitions are rejected.
Broken references are rejected.
Duplicate identifiers are rejected.
Display names cannot impersonate stable actor identifiers.
Old supported schema versions migrate or unsupported versions produce a clear error.
Malformed CLI requests fail with schema_validation_error before kernel start.
Malformed SQLite runtime payloads fail with schema_validation_error before kernel decode.
Plain-language requests without required fields route to intake_required.
Project resolution uses explicit project, first-run project, or authorized creation.
Registry routing assigns default Beings and permissions.
Retryable failure schedules retry, exhausted failure cancels downstream work.
Conflicting claims are preserved in reconciliation records.
Closeout creates durable closeout and learning records.
Structured human approval persists exact action, constraints, and expiration.
CLI dispatch, complete, handoff, evidence, verify, reject, and close run Priority 1 workflows.
CLI complete writes artifacts through the local filesystem adapter.
CLI model-draft writes bounded model drafts through the local filesystem adapter.
CLI model-draft blocks disabled OpenAI provider before network use.
CLI model-calls lists durable model-call audit records.
CLI failure-packets lists durable failure packets.
Model draft success records provider, model, actor, workstream, prompt hash, output hash, and artifact ID.
Model adapter failure records failure packets and failed model-call audit records.
Exported proof bundles include model-call records and failure packets.
SQLite mirror writes runs and runtime events while preserving JSON/JSONL artifacts.
SQLite-first load works without JSON run snapshots.
SQLite-first replay works without JSONL event logs.
CLI summaries expose dependency-safe execution batches.
CLI runs lists SQLite-backed runtime history.
```

## Known Limitations

```text
SQLite is now the preferred runtime load/replay authority, while JSON/JSONL remain audit artifacts.
Pydantic schema layer validates CLI requests and SQLite-loaded runtime payloads; kernel internals still use the Priority 1 dataclass model during gradual migration.
Canonical policy registry is wired into dispatch, evidence attachment, verification, and closeout. Release checks exact approval scope, expiration, and artifact hash when supplied. Memory-write, governance-policy modification, destructive-action, denied tool-use, and sensitive public-boundary attempts are explicitly blocked. Policy decisions persist on run records and SQLite. Priority 4 evidence-lock bridge covers artifact hash validation, verification records, first-class claim evidence status checks, queryable claim records, workstream claim-to-evidence links, and targeted per-claim evidence links.
Claim-to-evidence links support explicit claim IDs and conservative exact-phrase matching from evidence summary text.
No actual worker-level parallel execution yet; deterministic batch planning is available.
Live OpenAI API calls require local config and `OPENAI_API_KEY`; browser and external app adapters are not implemented.
Reconciliation detects simple `key=value` conflicts and first-class claim evidence-status conflicts.
Markdown import covers core project packet files, workstream README files, evidence files, deliverables, closeout, learning, and evidence-status claim tables. Freeform claim extraction remains future work.
```

## Local Model Config

```json
{
  "model_adapters": {
    "openai_compatible_local": {
      "enabled": true,
      "base_url": "http://192.168.1.48:1234/v1",
      "api_key_env": "",
      "allowed_models": ["*"],
      "max_prompt_chars": 12000,
      "max_output_chars": 8000
    },
    "openai": {
      "enabled": true,
      "api_key_env": "OPENAI_API_KEY",
      "allowed_models": ["gpt-5.6-luna"],
      "max_prompt_chars": 12000,
      "max_output_chars": 8000
    }
  }
}
```

Config path:

```text
.agencyos-runtime/config.local.json
```

Credential rule:

```text
Use environment variables for API keys. Do not commit secrets.
```

## Human Decisions

```text
Priority 2 is closed for the current repository shape.
Default Being routing is approved as-is.
Project creation requires human_owner_id.
Runtime storage supports JSON/JSONL and SQLite.
Policy source is hybrid: markdown for human view, JSON for executable policy.
Closeout accepts the baseline evidence standard.
Medium-risk external drafting may proceed, but sending pauses for approval.
Export implemented as portable proof bundle with verifier.
```
