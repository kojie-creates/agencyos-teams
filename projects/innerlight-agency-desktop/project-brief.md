# Project Brief

## Project Name

```text
innerlight-agency-desktop
```

## Owner

```text
Kojie
```

## Outcome

```text
Create and govern a cross-platform Electron desktop app for InnerLight Agency OS with BYOK Anthropic access, guided business intake, daily operating loop, embedded agent prompts, SQLite history, and packaging readiness.
```

## Why This Needs Teams

```text
This is a multi-lane product build with runtime implementation, agent prompt migration, credential handling, local persistence, UX flows, release packaging, and evidence review. Teams is appropriate because work can be split into independent workstreams while preserving shared governance, human approval gates, and closeout evidence.
```

## Success Criteria

```text
1. Existing desktop repo state is assessed before edits.
2. Electron, React, TypeScript, SQLite, Anthropic IPC, and local keystore paths build without TypeScript errors.
3. First-run setup, business wizard, daily loop, Ask Something, Evening Review, and history routes are verified locally.
4. Agent prompts are embedded from the canonical source folder with source/readback evidence.
5. Packaging config is present and Windows build is verified before any installer is treated as distributable.
6. Credential handling, external API use, package publishing, installer distribution, and destructive git actions remain human-approved.
```

## Non-Goals

```text
Do not overwrite uncommitted desktop repo work. Do not claim production readiness until live app launch, persistence, key storage, routing, API calls, packaging, and clean install behavior are verified. Do not migrate to Supabase. Do not expose API keys or commit local runtime secrets. Do not treat simulated API or UI checks as market or release evidence.
```
