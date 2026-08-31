import json
import sys
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))


@pytest.fixture
def runtime(tmp_path):
    from runtime_kernel.runtime import AgencyOSRuntime

    return AgencyOSRuntime(tmp_path / "runtime")


def test_runtime_completes_one_governed_codex_artifact_path(runtime):
    task = runtime.create_task(
        process_type="artifact_delivery",
        owner="operator-1",
        project="agencyos-one-bionic-codex-integration",
        workstream="runtime-kernel",
        requested_capability="artifact.write",
        authority="operator-1",
    )

    context = runtime.read_context(task["process_id"])
    created_receipt = runtime.last_receipt
    action = runtime.request_tool(
        task["process_id"],
        actor="operator-1",
        capability="artifact.write",
        credential_scopes=["artifact.write"],
    )
    artifact = runtime.write_artifact(
        task["process_id"],
        actor="codex",
        name="delivery.json",
        content={"result": "simulated codex output"},
    )
    event = runtime.log_event(
        task["process_id"],
        actor="codex",
        event_type="artifact_written",
    )
    closeout = runtime.closeout(task["process_id"], actor="operator-1")
    archived = runtime.archive(task["process_id"], actor="operator-1")

    assert context["status"] == "pending"
    assert created_receipt["policy_result"] == "NOT_EVALUATED"
    assert runtime.verify_receipt(created_receipt["request_id"])["verified"] is True
    assert action["status"] == "running"
    assert action["driver"] == "stub-codex-driver"
    assert action["driver_action"]["status"] == "SIMULATED"
    assert artifact["artifact_reference"]
    assert artifact["manifest_reference"]
    assert event["event_reference"]
    assert closeout["status"] == "complete"
    assert closeout["receipt"]["state_transition"] == "running->complete"
    assert runtime.read_context(task["process_id"])["status"] == "archived"
    assert archived["receipt"]["state_transition"] == "complete->archived"
    assert runtime.verify_receipt(closeout["receipt"]["request_id"])["verified"] is True

    ledger_entries = [
        json.loads(line)
        for line in runtime.event_ledger_path.read_text(encoding="utf-8").splitlines()
    ]
    assert ledger_entries[-2]["event_type"] == "closeout"
    assert ledger_entries[-2]["state_transition"] == "running->complete"
    assert ledger_entries[-1]["state_transition"] == "complete->archived"


@pytest.mark.parametrize(
    ("authority", "capability", "scopes", "external", "reason"),
    [
        (None, "artifact.write", ["artifact.write"], False, "MISSING_AUTHORITY"),
        ("operator-1", "network.delete", ["network.delete"], False, "DISALLOWED_CAPABILITY"),
        ("operator-1", "artifact.write", [], False, "INVALID_CREDENTIAL_SCOPE"),
        ("operator-1", "external.publish", ["external.publish"], True, "UNSAFE_EXTERNAL_ACTION"),
    ],
)
def test_policy_failure_denies_downstream_action(
    runtime, authority, capability, scopes, external, reason
):
    task = runtime.create_task(
        process_type="artifact_delivery",
        owner="operator-1",
        project="agencyos-one-bionic-codex-integration",
        workstream="runtime-kernel",
        requested_capability=capability,
        authority=authority,
    )

    result = runtime.request_tool(
        task["process_id"],
        actor="operator-1",
        capability=capability,
        credential_scopes=scopes,
        external=external,
    )

    assert result["status"] == "blocked"
    assert result["policy_result"] == "FAIL"
    assert result["reason"] == reason
    assert result["driver_action"] is None


def test_human_approval_requirement_halts_then_allows_action(runtime):
    task = runtime.create_task(
        process_type="artifact_delivery",
        owner="operator-1",
        project="agencyos-one-bionic-codex-integration",
        workstream="runtime-kernel",
        requested_capability="external.publish",
        authority="operator-1",
    )

    flagged = runtime.request_tool(
        task["process_id"],
        actor="operator-1",
        capability="external.publish",
        credential_scopes=["external.publish"],
    )
    invalid_approval = runtime.request_approval(
        task["process_id"], approved_by="untrusted-operator"
    )
    approval = runtime.request_approval(task["process_id"], approved_by="operator-1")
    resumed = runtime.request_tool(
        task["process_id"],
        actor="operator-1",
        capability="external.publish",
        credential_scopes=["external.publish"],
    )

    assert flagged["status"] == "blocked"
    assert flagged["policy_result"] == "FLAGGED"
    assert flagged["driver_action"] is None
    assert invalid_approval["status"] == "blocked"
    assert invalid_approval["reason"] == "UNAUTHORIZED_APPROVER"
    assert approval["status"] == "approved"
    assert resumed["status"] == "running"
    assert resumed["driver_action"]["status"] == "SIMULATED"


def test_blocked_process_denies_reentry_until_authorized_approval(runtime):
    task = runtime.create_task(
        process_type="artifact_delivery",
        owner="operator-1",
        project="agencyos-one-bionic-codex-integration",
        workstream="runtime-kernel",
        requested_capability="external.publish",
        authority="operator-1",
    )
    runtime.request_tool(
        task["process_id"],
        actor="operator-1",
        capability="external.publish",
        credential_scopes=["external.publish"],
    )

    reentry = runtime.request_tool(
        task["process_id"],
        actor="operator-1",
        capability="artifact.write",
        credential_scopes=["artifact.write"],
    )

    assert reentry["status"] == "blocked"
    assert reentry["reason"] == "PROCESS_BLOCKED"
    assert reentry["driver_action"] is None


def test_invalid_transitions_are_rejected(runtime):
    task = runtime.create_task(
        process_type="artifact_delivery",
        owner="operator-1",
        project="agencyos-one-bionic-codex-integration",
        workstream="runtime-kernel",
        requested_capability="artifact.write",
        authority="operator-1",
    )

    with pytest.raises(ValueError, match="running"):
        runtime.write_artifact(
            task["process_id"], actor="codex", name="delivery.json", content={}
        )
    with pytest.raises(ValueError, match="running"):
        runtime.closeout(task["process_id"], actor="operator-1")
    with pytest.raises(ValueError, match="complete"):
        runtime.archive(task["process_id"], actor="operator-1")


def test_receipt_manifest_linkage_survives_runtime_restart(runtime):
    from runtime_kernel.runtime import AgencyOSRuntime

    task = runtime.create_task(
        process_type="artifact_delivery",
        owner="operator-1",
        project="agencyos-one-bionic-codex-integration",
        workstream="runtime-kernel",
        requested_capability="artifact.write",
        authority="operator-1",
    )
    receipt = runtime.last_receipt
    stored_receipt = json.loads(
        (runtime.receipt_path / f"{receipt['request_id']}.json").read_text(
            encoding="utf-8"
        )
    )

    restarted_runtime = AgencyOSRuntime(runtime.root_path)
    verification = restarted_runtime.verify_receipt(receipt["request_id"])

    assert stored_receipt["receipt_manifest_reference"] == receipt[
        "receipt_manifest_reference"
    ]
    assert verification["verified"] is True


def test_runtime_boundary_documentation_labels_proof_and_simulation():
    documentation = (PROJECT_ROOT / "docs" / "runtime-kernel-v0.1.md").read_text(
        encoding="utf-8"
    )

    assert "## Proven" in documentation
    assert "## Simulated" in documentation
    assert "## Not Claimed" in documentation
    assert "production governance" in documentation
    assert "live external integrations" in documentation


def test_unauthorized_closeout_and_archive_are_blocked(runtime):
    task = runtime.create_task(
        process_type="artifact_delivery",
        owner="operator-1",
        project="agencyos-one-bionic-codex-integration",
        workstream="runtime-kernel",
        requested_capability="artifact.write",
        authority="operator-1",
    )
    runtime.request_tool(
        task["process_id"],
        actor="operator-1",
        capability="artifact.write",
        credential_scopes=["artifact.write"],
    )
    runtime.write_artifact(
        task["process_id"], actor="codex", name="delivery.json", content={}
    )

    with pytest.raises(ValueError, match="authority"):
        runtime.closeout(task["process_id"], actor="untrusted-operator")

    runtime.closeout(task["process_id"], actor="operator-1")

    with pytest.raises(ValueError, match="authority"):
        runtime.archive(task["process_id"], actor="untrusted-operator")

    assert runtime.read_context(task["process_id"])["status"] == "complete"


def test_fail_state_cannot_be_approved(runtime):
    task = runtime.create_task(
        process_type="artifact_delivery",
        owner="operator-1",
        project="agencyos-one-bionic-codex-integration",
        workstream="runtime-kernel",
        requested_capability="artifact.write",
        authority="operator-1",
    )
    runtime.request_tool(
        task["process_id"],
        actor="operator-1",
        capability="artifact.write",
        credential_scopes=[],
    )

    approval = runtime.request_approval(task["process_id"], approved_by="operator-1")

    assert approval["status"] == "blocked"
    assert approval["reason"] == "REMEDIATION_REQUIRED"
    assert runtime.read_context(task["process_id"])["status"] == "blocked"


def test_closeout_requires_written_artifact_not_generic_event_evidence(runtime):
    task = runtime.create_task(
        process_type="artifact_delivery",
        owner="operator-1",
        project="agencyos-one-bionic-codex-integration",
        workstream="runtime-kernel",
        requested_capability="artifact.write",
        authority="operator-1",
    )
    runtime.request_tool(
        task["process_id"],
        actor="operator-1",
        capability="artifact.write",
        credential_scopes=["artifact.write"],
    )
    runtime.log_event(task["process_id"], actor="codex", event_type="driver_finished")

    with pytest.raises(ValueError, match="Artifact evidence"):
        runtime.closeout(task["process_id"], actor="operator-1")


def test_tool_request_capability_must_match_process_capability(runtime):
    task = runtime.create_task(
        process_type="artifact_delivery",
        owner="operator-1",
        project="agencyos-one-bionic-codex-integration",
        workstream="runtime-kernel",
        requested_capability="artifact.write",
        authority="operator-1",
    )

    result = runtime.request_tool(
        task["process_id"],
        actor="operator-1",
        capability="external.publish",
        credential_scopes=["external.publish"],
    )

    assert result["status"] == "blocked"
    assert result["policy_result"] == "FAIL"
    assert result["reason"] == "CAPABILITY_MISMATCH"
    assert result["driver_action"] is None


def test_event_manifest_remains_verifiable_after_later_events(runtime):
    task = runtime.create_task(
        process_type="artifact_delivery",
        owner="operator-1",
        project="agencyos-one-bionic-codex-integration",
        workstream="runtime-kernel",
        requested_capability="artifact.write",
        authority="operator-1",
    )
    runtime.request_tool(
        task["process_id"],
        actor="operator-1",
        capability="artifact.write",
        credential_scopes=["artifact.write"],
    )
    first_event = runtime.log_event(
        task["process_id"], actor="codex", event_type="artifact_written"
    )
    runtime.log_event(task["process_id"], actor="codex", event_type="notification_sent")

    assert runtime.verify_receipt(first_event["receipt"]["request_id"])["verified"] is True


@pytest.mark.parametrize("kind", ["artifact", "event"])
def test_receipt_verification_detects_related_manifest_tampering(runtime, kind):
    task = runtime.create_task(
        process_type="artifact_delivery",
        owner="operator-1",
        project="agencyos-one-bionic-codex-integration",
        workstream="runtime-kernel",
        requested_capability="artifact.write",
        authority="operator-1",
    )
    runtime.request_tool(
        task["process_id"],
        actor="operator-1",
        capability="artifact.write",
        credential_scopes=["artifact.write"],
    )
    if kind == "artifact":
        result = runtime.write_artifact(
            task["process_id"], actor="codex", name="delivery.json", content={}
        )
        related_file = Path(result["artifact_reference"])
    else:
        result = runtime.log_event(
            task["process_id"], actor="codex", event_type="artifact_written"
        )
        manifest = runtime.manifest_service.get_manifest(result["manifest_reference"])
        related_file = Path(manifest["source_file"])

    related_file.write_text("tampered", encoding="utf-8")

    assert runtime.verify_receipt(result["receipt"]["request_id"])["verified"] is False
