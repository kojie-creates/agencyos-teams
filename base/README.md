# AgencyOS One Base

This folder holds shared, byte-identical material extracted from:

```text
agencyos-being-core/
agencyos-being-custom/
```

Use `base/` as the common anatomy layer for AgencyOS One.

## Shared Anatomy

The following folders were exact matches and now live here as the canonical shared copy:

```text
body/
history/
intelligence/
memory/
personal/
portfolio/
presence/
skeleton/
sources/
```

The following files were exact matches and now live here as the canonical shared copy:

```text
BOUNDARIES.md
EVOLUTION-RULES.md
INSTALLATION-RULES.md
```

## Active Difference

`agencyos-being-core/` now keeps the template-specific material.

`agencyos-being-custom/` now keeps the installed/custom material.

Folders that differed were not extracted:

```text
governance/
personality/
skills/
```

Those remain in Core or Custom because their contents are not identical.

## Redundant Copy Note

`_redundant-custom-copy/` contains the exact Custom copies that were moved out of the active Custom folder.

They are preserved only because recursive deletion was blocked by the local shell safety policy. They can be deleted later if you want a stricter cleanup.
