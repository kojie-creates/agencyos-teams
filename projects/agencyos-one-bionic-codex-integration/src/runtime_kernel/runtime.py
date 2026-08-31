"""Local, single-process governed runtime simulation."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from platform_governance.manifest_service import ManifestService
from platform_governance.policy_gate import PolicyGate


class StubCodexDriver:
    """Controlled stand-in for a Codex action boundary."""

    name = "stub-codex-driver"

    def execute(self, process_id: str, capability: str) -> dict:
        return {
            "status": "SIMULATED",
            "process_id": process_id,
            "capability": capability,
            "driver": self.name,
        }


class AgencyOSRuntime:
    """Runs the bounded Runtime Kernel v0.1 task lifecycle locally."""

    ALLOWED_CAPABILITIES = {"artifact.write", "external.publish"}
    HIGH_RISK_CAPABILITIES = {"external.publish"}

    def __init__(self, root_path: str | Path):
        self.root_path = Path(root_path)
        self.artifact_path = self.root_path / "artifacts"
        self.receipt_path = self.root_path / "receipts"
        self.event_ledger_path = self.root_path / "events.jsonl"
        self.event_path = self.root_path / "events"
        self.processes: dict[str, dict] = {}
        self.last_receipt: dict | None = None
        self.policy_gate = PolicyGate()
        self.driver = StubCodexDriver()
        self.manifest_service = ManifestService(self.root_path / "manifests")
        self.root_path.mkdir(parents=True, exist_ok=True)

    def create_task(
        self,
        *,
        process_type: str,
        owner: str,
        project: str,
        workstream: str,
        requested_capability: str,
        authority: str | None,
    ) -> dict:
        now = self._timestamp()
        process_id = f"proc-{uuid4().hex}"
        process = {
            "process_id": process_id,
            "process_type": process_type,
            "owner": owner,
            "project": project,
            "workstream": workstream,
            "status": "pending",
            "requested_capability": requested_capability,
            "authority": authority,
            "permission_result": None,
            "evidence_references": [],
            "artifact_evidence_references": [],
            "created_at": now,
            "updated_at": now,
            "approval_granted": False,
        }
        self.processes[process_id] = process
        self._record_receipt(
            process,
            actor=owner,
            capability=requested_capability,
            policy_result="NOT_EVALUATED",
            state_transition="created->pending",
        )
        return self.read_context(process_id)

    def read_context(self, process_id: str) -> dict:
        return dict(self._process(process_id))

    def request_tool(
        self,
        process_id: str,
        *,
        actor: str,
        capability: str,
        credential_scopes: list[str],
        external: bool = False,
    ) -> dict:
        process = self._process(process_id)
        if process["status"] == "blocked":
            receipt = self._record_receipt(
                process,
                actor=actor,
                capability=capability,
                policy_result=process["permission_result"] or "FAIL",
                state_transition="blocked->blocked",
            )
            return {
                "status": "blocked",
                "policy_result": process["permission_result"] or "FAIL",
                "reason": "PROCESS_BLOCKED",
                "driver_action": None,
                "receipt": receipt,
            }
        if process["status"] not in {"pending", "approved"}:
            raise ValueError(f"Tool requests are not allowed from {process['status']}.")
        decision = self._evaluate_policy(process, capability, credential_scopes, external)
        process["permission_result"] = decision["policy_result"]

        if decision["policy_result"] != "PASS":
            self._transition(process, "blocked")
            process["block_reason"] = decision["reason"]
            receipt = self._record_receipt(
                process,
                actor=actor,
                capability=capability,
                policy_result=decision["policy_result"],
                state_transition="request->blocked",
            )
            return {
                "status": "blocked",
                "policy_result": decision["policy_result"],
                "reason": decision["reason"],
                "driver_action": None,
                "receipt": receipt,
            }

        process.pop("block_reason", None)
        self._transition(process, "approved")
        driver_action = self.driver.execute(process_id, capability)
        self._transition(process, "running")
        receipt = self._record_receipt(
            process,
            actor=actor,
            capability=capability,
            policy_result="PASS",
            state_transition="approved->running",
            driver=self.driver.name,
        )
        return {
            "status": "running",
            "policy_result": "PASS",
            "driver": self.driver.name,
            "driver_action": driver_action,
            "receipt": receipt,
        }

    def write_artifact(
        self,
        process_id: str,
        *,
        actor: str,
        name: str,
        content: dict,
    ) -> dict:
        process = self._process(process_id)
        self._require_status(process, "running")
        self.artifact_path.mkdir(parents=True, exist_ok=True)
        artifact = self.artifact_path / f"{process_id}-{name}"
        artifact.write_text(json.dumps(content, indent=2), encoding="utf-8")
        manifest_reference = self.manifest_service.log_manifest(
            source_file=str(artifact),
            status="RUNTIME_ARTIFACT_WRITTEN",
            transaction_metadata={"process_id": process_id, "actor": actor},
        )
        process["evidence_references"].extend([str(artifact), manifest_reference])
        process["artifact_evidence_references"].append(str(artifact))
        receipt = self._record_receipt(
            process,
            actor=actor,
            capability="artifact.write",
            policy_result="PASS",
            state_transition="running->running",
            artifact_references=[str(artifact)],
            manifest_reference=manifest_reference,
        )
        return {
            "artifact_reference": str(artifact),
            "manifest_reference": manifest_reference,
            "receipt": receipt,
        }

    def log_event(
        self,
        process_id: str,
        *,
        actor: str,
        event_type: str,
        state_transition: str | None = None,
    ) -> dict:
        process = self._process(process_id)
        entry = {
            "event_id": f"evt-{uuid4().hex}",
            "process_id": process_id,
            "actor": actor,
            "event_type": event_type,
            "state_transition": state_transition or f"{process['status']}->{process['status']}",
            "timestamp": self._timestamp(),
        }
        with self.event_ledger_path.open("a", encoding="utf-8") as ledger:
            ledger.write(json.dumps(entry) + "\n")
        self.event_path.mkdir(parents=True, exist_ok=True)
        event_file = self.event_path / f"{entry['event_id']}.json"
        event_file.write_text(json.dumps(entry, indent=2), encoding="utf-8")
        manifest_reference = self.manifest_service.log_manifest(
            source_file=str(event_file),
            status="RUNTIME_EVENT_LEDGER_WRITTEN",
            transaction_metadata={
                "process_id": process_id,
                "event_id": entry["event_id"],
                "event_type": event_type,
            },
        )
        process["evidence_references"].append(manifest_reference)
        receipt = self._record_receipt(
            process,
            actor=actor,
            capability=process["requested_capability"],
            policy_result=process["permission_result"] or "PASS",
            state_transition=entry["state_transition"],
            artifact_references=[str(event_file)],
            manifest_reference=manifest_reference,
        )
        return {
            "event_reference": entry["event_id"],
            "manifest_reference": manifest_reference,
            "receipt": receipt,
        }

    def request_approval(self, process_id: str, *, approved_by: str) -> dict:
        process = self._process(process_id)
        self._require_status(process, "blocked")
        if approved_by != process["authority"]:
            receipt = self._record_receipt(
                process,
                actor=approved_by,
                capability=process["requested_capability"],
                policy_result=process["permission_result"] or "FLAGGED",
                state_transition="blocked->blocked",
            )
            return {
                "status": "blocked",
                "reason": "UNAUTHORIZED_APPROVER",
                "receipt": receipt,
            }
        if (
            process["permission_result"] != "FLAGGED"
            or process.get("block_reason") != "HUMAN_APPROVAL_REQUIRED"
        ):
            receipt = self._record_receipt(
                process,
                actor=approved_by,
                capability=process["requested_capability"],
                policy_result=process["permission_result"] or "FAIL",
                state_transition="blocked->blocked",
            )
            return {
                "status": "blocked",
                "reason": "REMEDIATION_REQUIRED",
                "receipt": receipt,
            }
        process["approval_granted"] = True
        process.pop("block_reason", None)
        self._transition(process, "approved")
        receipt = self._record_receipt(
            process,
            actor=approved_by,
            capability=process["requested_capability"],
            policy_result="PASS",
            state_transition="blocked->approved",
        )
        return {"status": "approved", "receipt": receipt}

    def closeout(self, process_id: str, *, actor: str) -> dict:
        process = self._process(process_id)
        self._require_status(process, "running")
        self._require_authority(process, actor)
        if not process["artifact_evidence_references"]:
            raise ValueError("Artifact evidence is required before closeout.")
        self._transition(process, "complete")
        receipt = self._record_receipt(
            process,
            actor=actor,
            capability=process["requested_capability"],
            policy_result=process["permission_result"] or "PASS",
            state_transition="running->complete",
            artifact_references=list(process["artifact_evidence_references"]),
        )
        event = self.log_event(
            process_id,
            actor=actor,
            event_type="closeout",
            state_transition="running->complete",
        )
        return {"status": "complete", "receipt": receipt, "event": event}

    def archive(self, process_id: str, *, actor: str) -> dict:
        """Archive a completed process after closeout evidence is recorded."""
        process = self._process(process_id)
        self._require_status(process, "complete")
        self._require_authority(process, actor)
        self._transition(process, "archived")
        receipt = self._record_receipt(
            process,
            actor=actor,
            capability=process["requested_capability"],
            policy_result=process["permission_result"] or "PASS",
            state_transition="complete->archived",
            artifact_references=list(process["evidence_references"]),
        )
        event = self.log_event(
            process_id,
            actor=actor,
            event_type="archived",
            state_transition="complete->archived",
        )
        return {"status": "archived", "receipt": receipt, "event": event}

    def _evaluate_policy(
        self,
        process: dict,
        capability: str,
        credential_scopes: list[str],
        external: bool,
    ) -> dict:
        if capability != process["requested_capability"]:
            return {"policy_result": "FAIL", "reason": "CAPABILITY_MISMATCH"}
        base = self.policy_gate.evaluate(capability).to_dict()
        if base["status"] != "PASS":
            return {"policy_result": base["status"], "reason": base["reason"]}
        if not process["authority"]:
            return {"policy_result": "FAIL", "reason": "MISSING_AUTHORITY"}
        if capability not in self.ALLOWED_CAPABILITIES:
            return {"policy_result": "FAIL", "reason": "DISALLOWED_CAPABILITY"}
        if capability not in credential_scopes:
            return {"policy_result": "FAIL", "reason": "INVALID_CREDENTIAL_SCOPE"}
        if external:
            return {"policy_result": "FAIL", "reason": "UNSAFE_EXTERNAL_ACTION"}
        if capability in self.HIGH_RISK_CAPABILITIES and not process["approval_granted"]:
            return {"policy_result": "FLAGGED", "reason": "HUMAN_APPROVAL_REQUIRED"}
        return {"policy_result": "PASS", "reason": "APPROVED"}

    def _record_receipt(
        self,
        process: dict,
        *,
        actor: str,
        capability: str,
        policy_result: str,
        state_transition: str,
        driver: str | None = None,
        artifact_references: list[str] | None = None,
        manifest_reference: str | None = None,
    ) -> dict:
        receipt = {
            "request_id": f"req-{uuid4().hex}",
            "process_id": process["process_id"],
            "actor": actor,
            "requested_capability": capability,
            "policy_result": policy_result,
            "driver": driver,
            "artifact_references": artifact_references or [],
            "state_transition": state_transition,
            "timestamp": self._timestamp(),
        }
        if manifest_reference:
            receipt["related_manifest_reference"] = manifest_reference
        self.receipt_path.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(receipt, sort_keys=True).encode("utf-8")
        receipt["sha256"] = hashlib.sha256(payload).hexdigest()
        receipt_file = self.receipt_path / f"{receipt['request_id']}.json"
        evidence_file = self.receipt_path / f"{receipt['request_id']}.evidence.json"
        evidence_file.write_bytes(payload)
        receipt_manifest_reference = self.manifest_service.log_manifest(
            source_file=str(evidence_file),
            status="RUNTIME_RECEIPT_WRITTEN",
            transaction_metadata={
                "process_id": process["process_id"],
                "request_id": receipt["request_id"],
                "state_transition": state_transition,
            },
        )
        receipt["receipt_manifest_reference"] = receipt_manifest_reference
        receipt_file.write_text(json.dumps(receipt, indent=2), encoding="utf-8")
        self.last_receipt = receipt
        return receipt

    def verify_receipt(self, request_id: str) -> dict:
        """Verify a receipt body and its local hash-backed manifest."""
        receipt_file = self.receipt_path / f"{request_id}.json"
        receipt = json.loads(receipt_file.read_text(encoding="utf-8"))
        manifest_reference = receipt.pop("receipt_manifest_reference")
        expected_receipt_hash = receipt.pop("sha256")
        canonical_payload = json.dumps(receipt, sort_keys=True).encode("utf-8")
        actual_receipt_hash = hashlib.sha256(canonical_payload).hexdigest()
        manifest = self.manifest_service.get_manifest(manifest_reference)
        source_file = Path(manifest["source_file"])
        manifest_hash_matches = (
            source_file.read_bytes() == canonical_payload
            and manifest["sha256"] == hashlib.sha256(source_file.read_bytes()).hexdigest()
        )
        related_manifest_matches = True
        related_manifest_reference = receipt.get("related_manifest_reference")
        if related_manifest_reference:
            related_manifest = self.manifest_service.get_manifest(
                related_manifest_reference
            )
            related_source = Path(related_manifest["source_file"])
            related_manifest_matches = (
                related_source.is_file()
                and related_manifest["sha256"]
                == hashlib.sha256(related_source.read_bytes()).hexdigest()
            )
        return {
            "verified": (
                expected_receipt_hash == actual_receipt_hash
                and manifest_hash_matches
                and related_manifest_matches
            ),
            "manifest_reference": manifest_reference,
        }

    def _process(self, process_id: str) -> dict:
        try:
            return self.processes[process_id]
        except KeyError as error:
            raise KeyError(f"Unknown process: {process_id}") from error

    def _transition(self, process: dict, status: str) -> None:
        process["status"] = status
        process["updated_at"] = self._timestamp()

    def _require_status(self, process: dict, expected: str) -> None:
        if process["status"] != expected:
            raise ValueError(f"Process must be {expected}, found {process['status']}.")

    @staticmethod
    def _require_authority(process: dict, actor: str) -> None:
        if actor != process["authority"]:
            raise ValueError("Actor does not match process authority.")

    @staticmethod
    def _timestamp() -> str:
        return datetime.now(timezone.utc).isoformat()
