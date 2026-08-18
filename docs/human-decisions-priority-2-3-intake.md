# Human Decisions Intake: Priority 2 and 3

Use this to finalize the decisions required before expanding beyond Priority 1.

## 1. Being Routing

Question:
Do you approve the current default Being routing?

Current default:

```text
intake / closeout -> being-jaavis
research -> being-atlas
build -> being-bob
operate -> being-maya
evidence / audit -> being-vera
verify -> being-truth
unknown workstream -> specialist-{workstream}
```

Decision:

```text
[x] Approve as-is
[ ] Approve with changes
[ ] Not approved
```

Changes:

```text

```

## 2. Project Creation Authority

Question:
Should new project creation always require a stable human owner identifier?

Recommended decision:

```text
Yes. Require human_owner_id for project creation.
```

Decision:

```text
[x] Yes, always require human_owner_id
[ ] No, allow system-created draft projects
[ ] Depends on project type
```

Notes:

```text

```

## 3. Durable Runtime Store

Question:
Which storage path should Priority 2 use?

Options:

```text
[ ] Keep JSON/JSONL only
[ ] Move to SQLite
[x] Support both JSON/JSONL and SQLite
```

Recommended decision:

```text
Support both: JSON/JSONL for transparency, SQLite for queryable runtime history.
```

Decision:

```text
Support both JSON/JSONL and SQLite.
```

## 4. Canonical Policy Source

Question:
Where should policy authority live before Priority 3 gate integration?

Options:

```text
[ ] Local markdown policy files
[ ] JSON/YAML policy registry
[ ] Python policy registry
[x] Hybrid: markdown for human-readable policy, JSON/YAML for executable policy
```

Recommended decision:

```text
Hybrid: markdown explains policy, JSON/YAML enforces policy.
```

Decision:

```text
Hybrid: markdown explains policy, JSON/YAML enforces policy.
```

## 5. Evidence Standards

Question:
What should count as valid evidence for closeout?

Baseline recommendation:

```text
Source artifact path.
Validation summary.
Reviewer identity.
Timestamp.
Claim-to-evidence mapping for any user-facing or external claim.
Human approval record when risk requires it.
```

Decision:

```text
[x] Accept baseline
[ ] Add requirements
[ ] Reduce requirements
```

Changes:

```text

```

## 6. Medium-Risk External Work

Question:
Should medium-risk external work pause for human approval?

Options:

```text
[ ] Yes, always pause
[ ] No, allow with warning and audit trail
[x] Pause only when sending externally, not when drafting
```

Recommended decision:

```text
Pause only when sending externally, not when drafting.
```

Decision:

```text
Pause only when sending externally, not when drafting.
```

## 7. Priority 1 CLI Completion Boundary

Question:
Are reject and export commands required before moving to Priority 2?

Options:

```text
[ ] Yes, add both before Priority 2
[x] Add reject only
[ ] Add export only
[ ] No, move to Priority 2 now
```

Recommended decision:

```text
Add reject only if human approval flows need explicit decline handling at CLI level. Export can wait.
```

Decision:

```text
Add reject before Priority 2. Export can wait.
```

Implementation status:

```text
CLI reject implemented. Export deferred.
```
