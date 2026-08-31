# AgencyOS Runtime Kernel v0.1

## Proven

- A local, single-process runtime can create a task, apply policy, run a stub Codex driver, write an artifact, append a JSONL event ledger entry, and issue local receipts.
- Artifact manifests contain SHA-256 hashes of their source files.
- Policy `FLAGGED` outcomes for `HUMAN_APPROVAL_REQUIRED` halt downstream driver execution until the recorded authority approves them. Policy `FAIL` outcomes require remediation or a new request and remain blocked.

## Simulated

- The Codex driver is a deterministic local stub.
- Runtime state, artifacts, receipts, ledger, and manifests are local filesystem outputs created during a run.
- The runtime is a controlled simulation milestone, not an interoperable model harness.

## Not Claimed

- production governance
- live external integrations
- live Hermes integration
- live AnythingLLM integration
- live Bionic scheduler integration
- multi-user administration
- full auth system
- durable Postgres persistence
- deployed API
- hardware operating system status
