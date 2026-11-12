# Project Plan

## Project Goal

```text
Build the InnerLight Agency OS desktop app through governed AgencyOS Teams execution, using the attached implementation plan as source context and C:\Users\felix\Desktop\InnerLight_Agency_Desktop as the target sidecar repo.
```

## Workstream Map

| Workstream | Purpose | Owner | Status |
| --- | --- | --- | --- |
| 01-runtime-foundation | Scaffold/build health, Electron main process, SQLite, IPC, keystore, Anthropic wrapper | Builder Copilot + Codex | Local build/test pass; scope gap open |
| 02-agent-routing | Read canonical agent prompts, embed TypeScript constants, classify signals, wire orchestrator/coordinator/specialist chain | Architect + Truth Agent | Open |
| 03-ui-operating-loop | Setup, wizard, home, session, signal badge, output cards, history, first-run routing | UX Designer + Builder Copilot | Open |
| 04-packaging-release | electron-builder config, icons, Windows installer, Mac packaging note, clean-machine verification | DevOps + QA Testing | Gated |
| 05-evidence-closeout | Evidence ledger, claim review, test output capture, release boundary, final human sign-off | Vera + Jaavis | Evidence started |

## Safe Parallel Work

```text
Runtime health checks, agent source inventory, UI route review, and packaging readiness assessment can proceed in parallel after current git state is captured. Prompt embedding must use current files from C:\Users\felix\Desktop\InnerLight_AgencyOS\.claude\agents and should not infer missing agents from the implementation plan alone.
```

## Gated Work

```text
External Anthropic API verification, installer distribution, package publishing, destructive git operations, credential movement, and any production-readiness claim require Kojie approval. Packaging claims require actual build output and install verification. API behavior claims require live call evidence or must be labeled simulated.
```

## Deliverables

```text
AgencyOS project packet, workstream briefs, desktop app implementation diffs, source prompt inventory, test/build evidence, packaging evidence, claim-boundary review, and closeout report.
```

## Timeline

```text
Phase 1: Assess current desktop repo and lock scope.
Phase 2: Restore or complete runtime foundation and IPC.
Phase 3: Complete agent routing and profile context injection.
Phase 4: Complete UI operating loop and history.
Phase 5: Package, verify, and prepare release gate.
```
