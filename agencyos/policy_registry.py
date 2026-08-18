"""Executable AgencyOS policy registry.

Priority 3 starts here: policy decisions become structured runtime objects
instead of scattered prose checks.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any


class PolicyOutcome(str, Enum):
    PERMIT = "permit"
    WARN = "warn"
    HOLD = "hold"
    BLOCK = "block"
    ESCALATE = "escalate"


@dataclass
class PolicyDecision:
    decision_id: str
    policy_version: str
    actor_id: str
    requested_action: str
    resource: str
    risk_level: str
    outcome: PolicyOutcome
    applicable_rules: list[str] = field(default_factory=list)
    required_conditions: list[str] = field(default_factory=list)
    missing_evidence: list[str] = field(default_factory=list)
    required_approval: str | None = None
    reason: str = ""
    timestamp: str = ""


@dataclass
class PolicyRule:
    rule_id: str
    actions: list[str]
    roles: list[str]
    outcome: PolicyOutcome
    reason: str
    risk_levels: list[str] = field(default_factory=list)
    required_approval: str | None = None
    required_evidence: list[str] = field(default_factory=list)


class PolicyRegistry:
    def __init__(self, version: str, rules: list[PolicyRule]):
        self.version = version
        self.rules = rules

    @classmethod
    def default(cls) -> "PolicyRegistry":
        return cls(
            version="agencyos.policy.v1",
            rules=[
                PolicyRule(
                    rule_id="internal_reversible_artifact_work_permitted",
                    actions=["write_local_artifact"],
                    roles=["research", "build", "operate", "operator", "evidence"],
                    risk_levels=["low"],
                    outcome=PolicyOutcome.PERMIT,
                    reason="Low-risk internal artifact work is permitted.",
                ),
                PolicyRule(
                    rule_id="external_action_requires_human_approval",
                    actions=["external_send", "publish", "release_external"],
                    roles=["operator", "research", "build", "operate", "evidence"],
                    risk_levels=["medium", "high", "critical"],
                    outcome=PolicyOutcome.HOLD,
                    required_approval="human",
                    reason="External action requires explicit human approval.",
                ),
                PolicyRule(
                    rule_id="verified_internal_closeout_permitted",
                    actions=["closeout"],
                    roles=["operator"],
                    risk_levels=["low"],
                    outcome=PolicyOutcome.PERMIT,
                    reason="Verified low-risk internal work may close out.",
                ),
                PolicyRule(
                    rule_id="internal_evidence_attachment_permitted",
                    actions=["attach_evidence"],
                    roles=["evidence", "operator"],
                    risk_levels=["low"],
                    outcome=PolicyOutcome.PERMIT,
                    reason="Low-risk evidence attachment is permitted.",
                ),
                PolicyRule(
                    rule_id="sensitive_evidence_requires_human_approval",
                    actions=["attach_sensitive_evidence"],
                    roles=["evidence", "operator"],
                    risk_levels=["low", "medium", "high", "critical"],
                    outcome=PolicyOutcome.HOLD,
                    required_approval="human",
                    reason="Sensitive evidence requires human approval.",
                ),
                PolicyRule(
                    rule_id="independent_verification_permitted",
                    actions=["verify"],
                    roles=["verifier", "truth", "evidence"],
                    risk_levels=["low"],
                    outcome=PolicyOutcome.PERMIT,
                    reason="Independent low-risk verification is permitted.",
                ),
                PolicyRule(
                    rule_id="memory_write_requires_explicit_policy_and_approval",
                    actions=["memory_write"],
                    roles=["operator", "research", "build", "operate", "evidence", "verifier"],
                    risk_levels=["low", "medium", "high", "critical"],
                    outcome=PolicyOutcome.BLOCK,
                    required_approval="human",
                    reason="Memory writes require explicit policy and approval.",
                ),
                PolicyRule(
                    rule_id="governance_policy_change_requires_designated_authority",
                    actions=["governance_policy_change"],
                    roles=["operator", "research", "build", "operate", "evidence", "verifier"],
                    risk_levels=["low", "medium", "high", "critical"],
                    outcome=PolicyOutcome.BLOCK,
                    required_approval="governance_authority",
                    reason="Governance policy changes require designated authority.",
                ),
                PolicyRule(
                    rule_id="destructive_action_requires_exact_target_authorization",
                    actions=["destructive_action"],
                    roles=["operator", "research", "build", "operate", "evidence", "verifier"],
                    risk_levels=["low", "medium", "high", "critical"],
                    outcome=PolicyOutcome.BLOCK,
                    required_approval="human",
                    reason="Destructive actions require exact target authorization.",
                ),
                PolicyRule(
                    rule_id="tool_use_requires_explicit_permission",
                    actions=["tool_use"],
                    roles=["operator", "research", "build", "operate", "evidence", "verifier"],
                    risk_levels=["low", "medium", "high", "critical"],
                    outcome=PolicyOutcome.BLOCK,
                    reason="Tool use requires explicit permission.",
                ),
                PolicyRule(
                    rule_id="sensitive_data_cannot_cross_public_boundary",
                    actions=["write_public_artifact"],
                    roles=["operator", "research", "build", "operate", "evidence"],
                    risk_levels=["high", "critical"],
                    outcome=PolicyOutcome.BLOCK,
                    reason="Sensitive data cannot cross public boundary.",
                ),
            ],
        )

    @classmethod
    def from_json(cls, path: Path) -> "PolicyRegistry":
        data = json.loads(path.read_text(encoding="utf-8"))
        return cls(
            version=data["version"],
            rules=[
                PolicyRule(
                    **{
                        **rule,
                        "outcome": PolicyOutcome(rule["outcome"]),
                    }
                )
                for rule in data.get("rules", [])
            ],
        )

    def to_json(self) -> str:
        return json.dumps(
            {
                "version": self.version,
                "rules": [
                    {
                        **asdict(rule),
                        "outcome": rule.outcome.value,
                    }
                    for rule in self.rules
                ],
            },
            indent=2,
        )

    def evaluate(
        self,
        actor_id: str,
        actor_roles: list[str],
        action: str,
        resource: str,
        risk_level: str,
        evidence_ids: list[str],
        approval_ids: list[str],
    ) -> PolicyDecision:
        if not actor_roles:
            return self._block(actor_id, action, resource, risk_level, "Unknown actor or missing roles.")

        for rule in self.rules:
            if action not in rule.actions:
                continue
            if not set(actor_roles).intersection(rule.roles):
                continue
            if rule.risk_levels and risk_level not in rule.risk_levels:
                continue
            missing_evidence = [item for item in rule.required_evidence if item not in evidence_ids]
            if missing_evidence:
                return self._decision(
                    actor_id,
                    action,
                    resource,
                    risk_level,
                    PolicyOutcome.HOLD,
                    [rule.rule_id],
                    missing_evidence=missing_evidence,
                    reason="Required evidence is missing.",
                )
            if rule.required_approval and not approval_ids:
                return self._decision(
                    actor_id,
                    action,
                    resource,
                    risk_level,
                    rule.outcome,
                    [rule.rule_id],
                    required_approval=rule.required_approval,
                    reason=rule.reason,
                )
            return self._decision(actor_id, action, resource, risk_level, rule.outcome, [rule.rule_id], reason=rule.reason)

        return self._block(actor_id, action, resource, risk_level, "No policy permits this action.")

    def _block(self, actor_id: str, action: str, resource: str, risk_level: str, reason: str) -> PolicyDecision:
        return self._decision(actor_id, action, resource, risk_level, PolicyOutcome.BLOCK, [], reason=reason)

    def _decision(
        self,
        actor_id: str,
        action: str,
        resource: str,
        risk_level: str,
        outcome: PolicyOutcome,
        applicable_rules: list[str],
        required_approval: str | None = None,
        missing_evidence: list[str] | None = None,
        reason: str = "",
    ) -> PolicyDecision:
        return PolicyDecision(
            decision_id=f"policy-decision-{uuid.uuid4().hex[:12]}",
            policy_version=self.version,
            actor_id=actor_id,
            requested_action=action,
            resource=resource,
            risk_level=risk_level,
            outcome=outcome,
            applicable_rules=applicable_rules,
            missing_evidence=missing_evidence or [],
            required_approval=required_approval,
            reason=reason,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )


def _encode(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, list):
        return [_encode(item) for item in value]
    if isinstance(value, dict):
        return {key: _encode(item) for key, item in value.items()}
    return value
