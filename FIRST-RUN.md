# First Run

Purpose:

```text
Gather the minimum startup context needed for AgencyOS Teams to begin useful work without repeatedly asking for the same setup details.
```

## Friendly Command Shape

Inside Codex, from this folder:

```text
@operator first-run
```

Meaning:

```text
Run the AgencyOS Teams startup sequence.
Gather installation context.
Create the first project packet.
Write FIRST-RUN-CONTEXT.md.
Write PROJECT-LINK.md.
Continue from the generated project.
```

## Direct Script

Interactive:

```text
python tools/first_run.py
```

Non-interactive:

```text
python tools/first_run.py --non-interactive --name "client-market-transition" --owner "Kojie" --outcome "Create research-to-GTM package"
```

## Outputs

```text
FIRST-RUN-CONTEXT.md
PROJECT-LINK.md
.first-run.json
projects/{project-name}/
```

## After First Run

Open:

```text
FIRST-RUN-CONTEXT.md
projects/{project-name}/intake.md
```

Then route the project through:

```text
agencyos-pro/getting-started-operator.md
```

## Automatic Diagnostic Intake

If the first-run request indicates a dev-team diagnostic lane for the user and work involved, first-run automatically starts:

```text
python tools/dev_team_diagnostic_intake.py
```

This collects diagnostic answers and upload paths before the project continues.

Skip only when needed:

```text
python tools/first_run.py --skip-dev-diagnostic
```

## Boundary

First-run can prepare context and create files.

It cannot approve external-facing, sensitive, paid, legal, financial, housing, medical, safety, memory, governance, or destructive actions.
