# Runtime Policy

Canonical executable policy:

```text
policies/runtime-policy.json
```

This markdown file is the human-readable view. The JSON policy is the executable source.

## Outcomes

```text
permit: allow the declared action.
warn: allow the action and record a risk notice.
hold: pause until a resolvable condition is satisfied.
block: prevent the action.
escalate: route the decision to the designated authority.
```

## Default Posture

```text
Unknown actors are blocked.
Unknown actions are blocked.
Missing roles are blocked.
Missing policy is blocked.
External actions hold for human approval.
Low-risk internal artifact work may proceed.
```

## Initial Rules

```text
internal_reversible_artifact_work_permitted
external_action_requires_human_approval
verified_internal_closeout_permitted
internal_evidence_attachment_permitted
sensitive_evidence_requires_human_approval
independent_verification_permitted
memory_write_requires_explicit_policy_and_approval
governance_policy_change_requires_designated_authority
destructive_action_requires_exact_target_authorization
tool_use_requires_explicit_permission
sensitive_data_cannot_cross_public_boundary
```
