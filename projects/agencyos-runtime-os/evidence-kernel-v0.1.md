# AgencyOS Runtime Kernel v0.1 Evidence

## Scope

This evidence covers the narrow local runtime milestone implemented under:

```text
projects/agencyos-one-bionic-codex-integration
```

## Files Added

```text
projects/agencyos-one-bionic-codex-integration/src/runtime_kernel/__init__.py
projects/agencyos-one-bionic-codex-integration/src/runtime_kernel/runtime.py
projects/agencyos-one-bionic-codex-integration/tests/test_runtime_kernel.py
projects/agencyos-one-bionic-codex-integration/docs/runtime-kernel-v0.1.md
```

## Verification

Focused runtime tests:

```text
python -m pytest projects\agencyos-one-bionic-codex-integration\tests\test_runtime_kernel.py -q
17 passed in 1.59s
```

Integration project tests:

```text
python -m pytest projects\agencyos-one-bionic-codex-integration\tests -q
65 passed in 2.92s
```

Compile check:

```text
python -m py_compile projects\agencyos-one-bionic-codex-integration\src\runtime_kernel\__init__.py projects\agencyos-one-bionic-codex-integration\src\runtime_kernel\runtime.py
passed
```

Whitespace check:

```text
git diff --check -- projects/agencyos-one-bionic-codex-integration/src/runtime_kernel projects/agencyos-one-bionic-codex-integration/tests/test_runtime_kernel.py projects/agencyos-one-bionic-codex-integration/docs/runtime-kernel-v0.1.md
passed after `git add -N` made the new files visible to diff checks; Git reported CRLF conversion warnings only.
```

## Review Evidence

Task review found a real halt bypass and evidence-linkage gaps.

Fix round 1 resolved blocked re-entry, closeout transition visibility, misleading task creation receipt, and missing transition tests.

Fix round 2 resolved persisted receipt-manifest linkage and restart-safe receipt verification.

Final scoped re-review verdict:

```text
ADDRESSED
Spec: PASS
Quality: PASS
```

Final whole-task review found additional authority and evidence issues. A final fix pass resolved:

- closeout/archive authority checks
- FAIL approval prevention
- artifact-only closeout requirement
- process capability binding
- per-event stable manifest sources
- related manifest verification
- documentation wording for FAIL vs FLAGGED

## Proven

- A task can be created through the runtime.
- Policy failures deny downstream driver execution.
- Human-approval requirements halt execution until authorized approval is recorded.
- An approved action calls a stub Codex driver.
- Artifact writes produce manifest references.
- Event ledger entries are written.
- Closeout produces observable `running->complete` evidence.
- Completed processes can be archived separately.
- Receipts are hash-backed and can be verified after a runtime restart.
- Unauthorized actors cannot close out or archive work.
- `FAIL` states cannot be approved as if they were human-review flags.
- Closeout requires artifact evidence from `write_artifact()`.
- Event evidence uses stable per-event files while JSONL remains convenience output.

## Simulated

- Codex driver is a local deterministic stub.
- Runtime state is in-memory during the active process.
- Artifacts, receipts, ledgers, and manifests are local filesystem outputs.
- No live Hermes, AnythingLLM, Bionic scheduler, external API, or deployed service was connected.

## Not Claimed

- Production governance.
- Autonomous self-governance.
- Hardware operating system status.
- Multi-user administration.
- Durable Postgres persistence.
- Full authentication system.
- Live external integration readiness.
