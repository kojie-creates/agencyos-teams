# Technical Diagnostic Workstream

Owner:

```text
@bob + @vera
```

Purpose:

```text
Turn the briefs into a concrete diagnostic path for the development team.
```

Intake script:

```text
python tools/dev_team_diagnostic_intake.py
```

Use Diana as named use case:

```text
python tools/dev_team_diagnostic_intake.py --use-case diana-spend-reporting-assistant
```

Primary Question:

```text
Are totals and percentages calculated before the AI sees the data, or is the AI calculating them itself?
```

Checks:

```text
Find extraction boundary.
Find normalization schema.
Find calculation owner.
Find validation checks.
Find report template owner.
Find AI prompt boundary.
Find tests for numeric drift.
```

Status:

```text
Started. Needs implementation evidence. Intake script created for collecting answers and uploads.
```
