# Governance Notes

Use the shared standard:

```text
../../governance/GOVERNANCE-STANDARD.md
```

## Project-Specific Rules

```text
1. Treat C:\Users\felix\Desktop\InnerLight_Agency_Desktop as the implementation repo and this project folder as the AgencyOS sidecar control packet.
2. Preserve existing uncommitted desktop repo changes unless Kojie explicitly asks to revert or replace them.
3. Read prompt source files before embedding. Source of truth is C:\Users\felix\Desktop\InnerLight_AgencyOS\.claude\agents.
4. Keep SQLite local. No Supabase dependency for this desktop app milestone.
5. Store only API-key verification status in evidence, never the key.
```

## External-Facing Boundaries

```text
This packet supports an internal governed build. It does not prove production readiness, security compliance, or distributable installer quality until the app is built, launched, exercised, packaged, installed, and reviewed with captured evidence.
```

## Evidence Requirements

```text
Capture command output for git status, npm install/build/test, Electron launch checks, prompt inventory, route behavior, SQLite persistence, keystore behavior, Anthropic API verification when approved, and installer output. Label manual inspection, simulated checks, and live API evidence separately.
```

## Human Approval Gates

```text
Kojie approval is required before external API calls, package publishing, installer distribution, destructive git operations, credential handling beyond local safeStorage, or public/commercial claims.
```
