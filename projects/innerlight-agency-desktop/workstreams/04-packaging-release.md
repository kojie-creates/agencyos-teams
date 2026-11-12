# Workstream 04: Packaging Release

## Purpose

Prepare Windows and Mac packaging through electron-builder while separating packaging configuration from distributable release evidence.

## Exit Criteria

- `electron-builder.yml` and icon assets exist.
- Windows installer build output is verified on this machine before any `.exe` claim.
- Mac `.dmg` remains pending unless built on a Mac or through an approved Mac build environment.
- Clean install behavior is verified before release language.

## Gate

No installer distribution, public release claim, or customer-facing package without Kojie approval.
