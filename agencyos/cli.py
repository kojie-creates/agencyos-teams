"""Command line entry point for the local AgencyOS Teams runtime."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import asdict
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from agencyos.project_importer import import_project_folder
from agencyos.schemas import Request as RuntimeRequest
from tools.enforcement_kernel import EnforcementKernel, KernelRequest, LifecycleState, TransitionError


def _encode(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, list):
        return [_encode(item) for item in value]
    if isinstance(value, dict):
        return {key: _encode(item) for key, item in value.items()}
    return value


def _write_json(payload: dict[str, Any]) -> None:
    print(json.dumps(_encode(payload), indent=2))


def _request_from_json(path: Path) -> KernelRequest:
    data = json.loads(path.read_text(encoding="utf-8"))
    try:
        RuntimeRequest(
            id=f"request-{data['request_id']}",
            actor_id=data["actor_id"],
            human_owner_id=data.get("human_owner_id", "human-unknown"),
            desired_outcome=data["requested_outcome"],
            definition_of_done=data.get("definition_of_done", []),
            allowed_tools=data.get("allowed_tools", []),
            off_limits_actions=data.get("off_limits_actions", []),
            approval_requirements=data.get("approval_requirements", []),
            source_inputs=data.get("source_inputs", []),
            sensitivity_classification="high" if data.get("sensitive") else "low",
        )
        if not data.get("required_workstreams"):
            raise ValueError("required_workstreams is required and must not be empty.")
    except (ValidationError, KeyError, ValueError) as exc:
        raise ValueError(f"schema_validation_error: {exc}") from exc
    return KernelRequest(**data)


def _run_summary(run) -> dict[str, Any]:
    return {
        "run_id": run.run_id,
        "project_id": run.project_id,
        "state": run.state,
        "risk_level": run.risk_level,
        "execution_mode": run.execution_mode,
        "execution_batches": run.execution_batches,
        "runnable_workstreams": [packet.workstream_id for packet in run.runnable_packets],
        "missing_evidence": run.missing_evidence,
        "block_reason": run.block_reason,
    }


def _next_actions(run) -> list[str]:
    if run.state == LifecycleState.READY:
        return ["dispatch_ready"]
    if run.state == LifecycleState.AWAITING_HUMAN:
        return ["approve", "reject"]
    if run.state == LifecycleState.EVIDENCE_REQUIRED:
        return ["attach_evidence"]
    if run.state == LifecycleState.APPROVED and run.risk_level.value == "high":
        return ["authorize_release"]
    if run.state == LifecycleState.CLOSED:
        return []
    return ["status"]


def cmd_run(args: argparse.Namespace) -> int:
    kernel = EnforcementKernel(Path(args.root))
    run = kernel.start(_request_from_json(Path(args.request)))
    _write_json(_run_summary(run))
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    kernel = EnforcementKernel(Path(args.root))
    run = kernel.store.load(args.run_id)
    payload = _run_summary(run)
    payload["next_actions"] = _next_actions(run)
    payload["status_report"] = kernel.status_report(args.run_id)
    _write_json(payload)
    return 0


def cmd_events(args: argparse.Namespace) -> int:
    kernel = EnforcementKernel(Path(args.root))
    events = [asdict(event) for event in kernel.replay(args.run_id)]
    _write_json({"run_id": args.run_id, "events": events})
    return 0


def cmd_runs(args: argparse.Namespace) -> int:
    kernel = EnforcementKernel(Path(args.root))
    _write_json({"runs": kernel.store.list_runs()})
    return 0


def cmd_policy_decisions(args: argparse.Namespace) -> int:
    kernel = EnforcementKernel(Path(args.root))
    _write_json({"run_id": args.run_id, "policy_decisions": kernel.store.policy_decisions(args.run_id)})
    return 0


def cmd_claim_records(args: argparse.Namespace) -> int:
    kernel = EnforcementKernel(Path(args.root))
    _write_json({"run_id": args.run_id, "claim_records": kernel.store.claim_records(args.run_id)})
    return 0


def cmd_model_calls(args: argparse.Namespace) -> int:
    kernel = EnforcementKernel(Path(args.root))
    run = kernel.store.load(args.run_id)
    _write_json({"run_id": args.run_id, "model_call_records": [asdict(record) for record in run.model_call_records]})
    return 0


def cmd_failure_packets(args: argparse.Namespace) -> int:
    kernel = EnforcementKernel(Path(args.root))
    run = kernel.store.load(args.run_id)
    _write_json({"run_id": args.run_id, "failure_packets": [asdict(packet) for packet in run.failure_packets]})
    return 0


def cmd_export_run(args: argparse.Namespace) -> int:
    kernel = EnforcementKernel(Path(args.root))
    run = kernel.store.load(args.run_id)
    events = [asdict(event) for event in kernel.replay(args.run_id)]
    bundle = {
        "schema_version": "agencyos.export.v1",
        "run": _run_summary(run),
        "request": asdict(run.request),
        "packets": [asdict(packet) for packet in run.packets],
        "artifacts": [asdict(artifact) for artifact in run.artifacts],
        "evidence": [asdict(item) for item in run.evidence],
        "claim_records": [asdict(claim) for claim in run.claim_records],
        "verification_records": [asdict(record) for record in run.verification_records],
        "policy_decisions": [asdict(decision) for decision in run.policy_decisions],
        "approval_records": [asdict(record) for record in run.approval_records],
        "model_call_records": [asdict(record) for record in run.model_call_records],
        "failure_packets": [asdict(packet) for packet in run.failure_packets],
        "closeout_records": [asdict(record) for record in run.closeout_records],
        "learning_records": [asdict(record) for record in run.learning_records],
        "events": events,
    }
    encoded_bundle = _encode(bundle)
    manifest_base = {
        "schema_version": "agencyos.export.manifest.v1",
        "counts": {
            "packets": len(bundle["packets"]),
            "artifacts": len(bundle["artifacts"]),
            "evidence": len(bundle["evidence"]),
            "claim_records": len(bundle["claim_records"]),
            "verification_records": len(bundle["verification_records"]),
            "policy_decisions": len(bundle["policy_decisions"]),
            "approval_records": len(bundle["approval_records"]),
            "model_call_records": len(bundle["model_call_records"]),
            "failure_packets": len(bundle["failure_packets"]),
            "closeout_records": len(bundle["closeout_records"]),
            "learning_records": len(bundle["learning_records"]),
            "events": len(bundle["events"]),
        },
        "artifact_hashes": [artifact["content_hash"] for artifact in encoded_bundle["artifacts"]],
    }
    hash_input = json.dumps(encoded_bundle, sort_keys=True, separators=(",", ":"))
    encoded_bundle["manifest"] = manifest_base | {
        "bundle_hash": f"sha256:{hashlib.sha256(hash_input.encode('utf-8')).hexdigest()}"
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(encoded_bundle, indent=2), encoding="utf-8")
    _write_json({"run_id": args.run_id, "output": str(output)})
    return 0


def cmd_verify_export(args: argparse.Namespace) -> int:
    bundle = json.loads(Path(args.input).read_text(encoding="utf-8"))
    manifest = bundle.get("manifest", {})
    required_sections = [
        "schema_version",
        "run",
        "request",
        "packets",
        "artifacts",
        "evidence",
        "claim_records",
        "verification_records",
        "policy_decisions",
        "approval_records",
        "model_call_records",
        "failure_packets",
        "closeout_records",
        "learning_records",
        "events",
        "manifest",
    ]
    required_sections_valid = all(section in bundle for section in required_sections)
    schema_valid = (
        bundle.get("schema_version") == "agencyos.export.v1"
        and manifest.get("schema_version") == "agencyos.export.manifest.v1"
    )
    expected_hash = manifest.get("bundle_hash", "")
    bundle_without_manifest = dict(bundle)
    bundle_without_manifest.pop("manifest", None)
    hash_input = json.dumps(bundle_without_manifest, sort_keys=True, separators=(",", ":"))
    actual_hash = f"sha256:{hashlib.sha256(hash_input.encode('utf-8')).hexdigest()}"
    artifact_hashes = [artifact.get("content_hash", "") for artifact in bundle.get("artifacts", [])]
    actual_counts = {
        "packets": len(bundle.get("packets", [])),
        "artifacts": len(bundle.get("artifacts", [])),
        "evidence": len(bundle.get("evidence", [])),
        "claim_records": len(bundle.get("claim_records", [])),
        "verification_records": len(bundle.get("verification_records", [])),
        "policy_decisions": len(bundle.get("policy_decisions", [])),
        "approval_records": len(bundle.get("approval_records", [])),
        "model_call_records": len(bundle.get("model_call_records", [])),
        "failure_packets": len(bundle.get("failure_packets", [])),
        "closeout_records": len(bundle.get("closeout_records", [])),
        "learning_records": len(bundle.get("learning_records", [])),
        "events": len(bundle.get("events", [])),
    }
    counts_valid = manifest.get("counts", {}) == actual_counts
    artifact_hashes_valid = manifest.get("artifact_hashes", []) == artifact_hashes
    artifact_content_hashes_valid = all(
        artifact.get("content_hash") == f"sha256:{hashlib.sha256(artifact.get('content', '').encode('utf-8')).hexdigest()}"
        for artifact in bundle.get("artifacts", [])
    )
    event_chain_valid = True
    previous_state = None
    for event in bundle.get("events", []):
        if event.get("from_state") != previous_state:
            event_chain_valid = False
            break
        previous_state = event.get("to_state")
    run_state_valid = not bundle.get("events") or previous_state == bundle.get("run", {}).get("state")
    run_id = bundle.get("run", {}).get("run_id")
    artifact_ids = {artifact.get("artifact_id") for artifact in bundle.get("artifacts", [])}
    evidence_ids = {item.get("evidence_id") for item in bundle.get("evidence", [])}
    claim_ids = {claim.get("claim_id") for claim in bundle.get("claim_records", [])}
    approval_ids = {record.get("approval_id") for record in bundle.get("approval_records", [])}
    references_valid = all(
        claim.get("artifact_id") in artifact_ids
        and set(claim.get("evidence_ids", [])).issubset(evidence_ids)
        for claim in bundle.get("claim_records", [])
    )
    references_valid = references_valid and all(
        set(artifact.get("evidence_ids", [])).issubset(evidence_ids)
        for artifact in bundle.get("artifacts", [])
    )
    references_valid = references_valid and all(
        record.get("artifact_id") in artifact_ids
        for record in bundle.get("verification_records", [])
    )
    references_valid = references_valid and all(
        record.get("artifact_id") in artifact_ids if record.get("artifact_id") else True
        for record in bundle.get("model_call_records", [])
    )
    references_valid = references_valid and all(
        set(record.get("artifact_ids", [])).issubset(artifact_ids)
        and set(record.get("evidence_ids", [])).issubset(evidence_ids)
        for record in bundle.get("closeout_records", [])
    )
    references_valid = references_valid and all(
        event.get("run_id") == run_id
        for event in bundle.get("events", [])
    )
    references_valid = references_valid and all(
        decision.get("decision_id") for decision in bundle.get("policy_decisions", [])
    )
    references_valid = references_valid and all(
        approval_id for approval_id in approval_ids
    )
    references_valid = references_valid and all(
        claim_id for claim_id in claim_ids
    )
    id_sections = {
        "artifacts": "artifact_id",
        "evidence": "evidence_id",
        "claim_records": "claim_id",
        "verification_records": "verification_id",
        "policy_decisions": "decision_id",
        "approval_records": "approval_id",
        "model_call_records": "model_call_id",
        "failure_packets": "failure_id",
        "closeout_records": "closeout_id",
        "learning_records": "learning_id",
        "events": "event_id",
    }
    duplicate_ids_valid = True
    for section, id_key in id_sections.items():
        ids = [item.get(id_key) for item in bundle.get(section, [])]
        if any(not item_id for item_id in ids) or len(ids) != len(set(ids)):
            duplicate_ids_valid = False
            break
    failed_checks = []
    if not schema_valid:
        failed_checks.append("schema")
    if not required_sections_valid:
        failed_checks.append("required_sections")
    if expected_hash != actual_hash:
        failed_checks.append("bundle_hash")
    if not artifact_hashes_valid:
        failed_checks.append("artifact_hashes")
    if not counts_valid:
        failed_checks.append("counts")
    if not artifact_content_hashes_valid:
        failed_checks.append("artifact_content_hashes")
    if not event_chain_valid:
        failed_checks.append("event_chain")
    if not run_state_valid:
        failed_checks.append("run_state")
    if not references_valid:
        failed_checks.append("references")
    if not duplicate_ids_valid:
        failed_checks.append("duplicate_ids")
    valid = (
        schema_valid
        and required_sections_valid
        and expected_hash == actual_hash
        and artifact_hashes_valid
        and counts_valid
        and artifact_content_hashes_valid
        and event_chain_valid
        and run_state_valid
        and references_valid
        and duplicate_ids_valid
    )
    _write_json(
        {
            "valid": valid,
            "schema_valid": schema_valid,
            "required_sections_valid": required_sections_valid,
            "bundle_hash": actual_hash,
            "expected_bundle_hash": expected_hash,
            "artifact_hashes_valid": artifact_hashes_valid,
            "counts_valid": counts_valid,
            "artifact_content_hashes_valid": artifact_content_hashes_valid,
            "event_chain_valid": event_chain_valid,
            "run_state_valid": run_state_valid,
            "references_valid": references_valid,
            "duplicate_ids_valid": duplicate_ids_valid,
            "failed_checks": failed_checks,
        }
    )
    return 0


def cmd_import_project(args: argparse.Namespace) -> int:
    registry = import_project_folder(Path(args.project), output_path=Path(args.output) if args.output else None)
    _write_json(
        {
            "project_id": registry.projects[0].id,
            "projects": len(registry.projects),
            "requests": len(registry.requests),
            "workstreams": len(registry.workstreams),
            "beings": len(registry.beings),
            "agencies": len(registry.agencies),
            "policies": len(registry.policies),
            "handoffs": len(registry.handoffs),
        }
    )
    return 0


def cmd_approve(args: argparse.Namespace) -> int:
    kernel = EnforcementKernel(Path(args.root))
    run = kernel.record_human_approval(
        args.run_id,
        approver_id=args.approver_id,
        decision=args.decision,
        rationale=args.rationale,
    )
    _write_json(_run_summary(run))
    return 0


def cmd_reject(args: argparse.Namespace) -> int:
    kernel = EnforcementKernel(Path(args.root))
    run = kernel.record_human_approval(
        args.run_id,
        approver_id=args.approver_id,
        decision="rejected",
        rationale=args.rationale,
    )
    _write_json(_run_summary(run))
    return 0


def cmd_close(args: argparse.Namespace) -> int:
    kernel = EnforcementKernel(Path(args.root))
    run = kernel.request_closeout(args.run_id, actor_id=args.actor_id)
    _write_json(_run_summary(run))
    return 0


def cmd_intake(args: argparse.Namespace) -> int:
    kernel = EnforcementKernel(Path(args.root))
    run = kernel.start_plain_text(args.text, actor_id=args.actor_id, human_owner_id=args.human_owner_id)
    _write_json(_run_summary(run) | {"intake_required": run.intake_required})
    return 0


def cmd_dispatch(args: argparse.Namespace) -> int:
    kernel = EnforcementKernel(Path(args.root))
    run = kernel.dispatch_ready(args.run_id)
    _write_json(_run_summary(run))
    return 0


def cmd_complete(args: argparse.Namespace) -> int:
    kernel = EnforcementKernel(Path(args.root))
    run = kernel.complete_artifact(
        args.run_id,
        args.workstream_id,
        args.path,
        args.content,
        actor_id=args.actor_id,
        claims=args.claim,
    )
    _write_json(_run_summary(run))
    return 0


def cmd_model_draft(args: argparse.Namespace) -> int:
    kernel = EnforcementKernel(Path(args.root))
    run = kernel.draft_model_artifact(
        args.run_id,
        args.workstream_id,
        args.path,
        prompt=args.prompt,
        model=args.model,
        actor_id=args.actor_id,
        provider=args.provider,
    )
    _write_json(_run_summary(run))
    return 0


def cmd_handoff(args: argparse.Namespace) -> int:
    kernel = EnforcementKernel(Path(args.root))
    run = kernel.create_handoff(args.run_id, actor_id=args.actor_id)
    _write_json(_run_summary(run))
    return 0


def cmd_evidence(args: argparse.Namespace) -> int:
    kernel = EnforcementKernel(Path(args.root))
    run = kernel.attach_evidence(
        args.run_id,
        args.workstream_id,
        args.path,
        args.summary,
        actor_id=args.actor_id,
        claim_ids=args.claim_id,
    )
    _write_json(_run_summary(run))
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    kernel = EnforcementKernel(Path(args.root))
    run = kernel.verify(args.run_id, reviewer_id=args.reviewer_id)
    _write_json(_run_summary(run))
    return 0


def cmd_release(args: argparse.Namespace) -> int:
    kernel = EnforcementKernel(Path(args.root))
    run = kernel.authorize_release(args.run_id, actor_id=args.actor_id)
    _write_json(_run_summary(run))
    return 0


def cmd_fail(args: argparse.Namespace) -> int:
    kernel = EnforcementKernel(Path(args.root))
    run = kernel.fail_work(
        args.run_id,
        args.workstream_id,
        actor_id=args.actor_id,
        error_type=args.error_type,
        error_message=args.error_message,
        retryable=args.retryable,
    )
    _write_json(_run_summary(run))
    return 0


def cmd_resume(args: argparse.Namespace) -> int:
    kernel = EnforcementKernel(Path(args.root))
    run = kernel.resume(args.run_id, actor_id=args.actor_id)
    _write_json(_run_summary(run))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="agencyos")
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run")
    run.add_argument("--root", default=".")
    run.add_argument("--request", required=True)
    run.set_defaults(func=cmd_run)

    status = sub.add_parser("status")
    status.add_argument("--root", default=".")
    status.add_argument("--run-id", required=True)
    status.set_defaults(func=cmd_status)

    events = sub.add_parser("events")
    events.add_argument("--root", default=".")
    events.add_argument("--run-id", required=True)
    events.set_defaults(func=cmd_events)

    runs = sub.add_parser("runs")
    runs.add_argument("--root", default=".")
    runs.set_defaults(func=cmd_runs)

    policy_decisions = sub.add_parser("policy-decisions")
    policy_decisions.add_argument("--root", default=".")
    policy_decisions.add_argument("--run-id", required=True)
    policy_decisions.set_defaults(func=cmd_policy_decisions)

    claim_records = sub.add_parser("claim-records")
    claim_records.add_argument("--root", default=".")
    claim_records.add_argument("--run-id", required=True)
    claim_records.set_defaults(func=cmd_claim_records)

    model_calls = sub.add_parser("model-calls")
    model_calls.add_argument("--root", default=".")
    model_calls.add_argument("--run-id", required=True)
    model_calls.set_defaults(func=cmd_model_calls)

    failure_packets = sub.add_parser("failure-packets")
    failure_packets.add_argument("--root", default=".")
    failure_packets.add_argument("--run-id", required=True)
    failure_packets.set_defaults(func=cmd_failure_packets)

    export_run = sub.add_parser("export-run")
    export_run.add_argument("--root", default=".")
    export_run.add_argument("--run-id", required=True)
    export_run.add_argument("--output", required=True)
    export_run.set_defaults(func=cmd_export_run)

    verify_export = sub.add_parser("verify-export")
    verify_export.add_argument("--input", required=True)
    verify_export.set_defaults(func=cmd_verify_export)

    import_project = sub.add_parser("import-project")
    import_project.add_argument("--project", required=True)
    import_project.add_argument("--output")
    import_project.set_defaults(func=cmd_import_project)

    approve = sub.add_parser("approve")
    approve.add_argument("--root", default=".")
    approve.add_argument("--run-id", required=True)
    approve.add_argument("--approver-id", required=True)
    approve.add_argument("--decision", choices=["approved", "rejected", "revise", "defer"], required=True)
    approve.add_argument("--rationale", required=True)
    approve.set_defaults(func=cmd_approve)

    reject = sub.add_parser("reject")
    reject.add_argument("--root", default=".")
    reject.add_argument("--run-id", required=True)
    reject.add_argument("--approver-id", required=True)
    reject.add_argument("--rationale", required=True)
    reject.set_defaults(func=cmd_reject)

    close = sub.add_parser("close")
    close.add_argument("--root", default=".")
    close.add_argument("--run-id", required=True)
    close.add_argument("--actor-id", required=True)
    close.set_defaults(func=cmd_close)

    intake = sub.add_parser("intake")
    intake.add_argument("--root", default=".")
    intake.add_argument("--text", required=True)
    intake.add_argument("--actor-id", required=True)
    intake.add_argument("--human-owner-id", required=True)
    intake.set_defaults(func=cmd_intake)

    dispatch = sub.add_parser("dispatch")
    dispatch.add_argument("--root", default=".")
    dispatch.add_argument("--run-id", required=True)
    dispatch.set_defaults(func=cmd_dispatch)

    complete = sub.add_parser("complete")
    complete.add_argument("--root", default=".")
    complete.add_argument("--run-id", required=True)
    complete.add_argument("--workstream-id", required=True)
    complete.add_argument("--path", required=True)
    complete.add_argument("--content", required=True)
    complete.add_argument("--actor-id", required=True)
    complete.add_argument("--claim", action="append", default=[])
    complete.set_defaults(func=cmd_complete)

    model_draft = sub.add_parser("model-draft")
    model_draft.add_argument("--root", default=".")
    model_draft.add_argument("--run-id", required=True)
    model_draft.add_argument("--workstream-id", required=True)
    model_draft.add_argument("--path", required=True)
    model_draft.add_argument("--prompt", required=True)
    model_draft.add_argument("--model", required=True)
    model_draft.add_argument("--provider", default="local_model_draft")
    model_draft.add_argument("--actor-id", required=True)
    model_draft.set_defaults(func=cmd_model_draft)

    handoff = sub.add_parser("handoff")
    handoff.add_argument("--root", default=".")
    handoff.add_argument("--run-id", required=True)
    handoff.add_argument("--actor-id", required=True)
    handoff.set_defaults(func=cmd_handoff)

    evidence = sub.add_parser("evidence")
    evidence.add_argument("--root", default=".")
    evidence.add_argument("--run-id", required=True)
    evidence.add_argument("--workstream-id", required=True)
    evidence.add_argument("--path", required=True)
    evidence.add_argument("--summary", required=True)
    evidence.add_argument("--actor-id", required=True)
    evidence.add_argument("--claim-id", action="append", default=[])
    evidence.set_defaults(func=cmd_evidence)

    verify = sub.add_parser("verify")
    verify.add_argument("--root", default=".")
    verify.add_argument("--run-id", required=True)
    verify.add_argument("--reviewer-id", required=True)
    verify.set_defaults(func=cmd_verify)

    release = sub.add_parser("release")
    release.add_argument("--root", default=".")
    release.add_argument("--run-id", required=True)
    release.add_argument("--actor-id", required=True)
    release.set_defaults(func=cmd_release)

    fail = sub.add_parser("fail")
    fail.add_argument("--root", default=".")
    fail.add_argument("--run-id", required=True)
    fail.add_argument("--workstream-id", required=True)
    fail.add_argument("--actor-id", required=True)
    fail.add_argument("--error-type", required=True)
    fail.add_argument("--error-message", required=True)
    fail.add_argument("--retryable", action="store_true")
    fail.set_defaults(func=cmd_fail)

    resume = sub.add_parser("resume")
    resume.add_argument("--root", default=".")
    resume.add_argument("--run-id", required=True)
    resume.add_argument("--actor-id", required=True)
    resume.set_defaults(func=cmd_resume)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except (TransitionError, FileNotFoundError, KeyError, ValueError, TypeError) as exc:
        print(json.dumps({"error": str(exc)}, indent=2), file=sys.stderr)
        return 1
