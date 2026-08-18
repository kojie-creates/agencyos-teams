# Project Intake

## Request

```text
@operator first-run for Diana's spend reporting assistant using customer briefs.
```

## Desired Outcome

```text
Create a routed AgencyOS Teams project packet for Diana's spend reporting assistant: stabilize calculation accuracy, separate deterministic metrics from AI narrative, and prepare executive plus dev-team next steps.
```

## Context

```text
Installation mode: standalone
Existing project path:
Active Being: Jaavis
Customer context: Diana is dealing with an automated spend reporting assistant that produces spend analysis, observations, cost-saving recommendations, and client-ready report text.
Current pain: reports often require manual correction because numerical interpretation, totals, formatting, or narrative alignment are unreliable.
Core design requirement: Diana enjoys interpreting spend, but calculations must be correct before analysis text is generated.
Likely architecture issue: AI appears to be asked to interpret raw data, calculate financial metrics, and write narrative in the same layer.
Target architecture: extraction -> normalization -> deterministic calculation -> verified metrics -> AI narrative.
Source PDFs:
- C:\Users\felix\Downloads\DianaBrief.md-1.pdf
- C:\Users\felix\Downloads\Diana_DevTeam.md-1.pdf
- C:\Users\felix\Downloads\Diana_ExecutiveTeam.md-1.pdf
```

## Constraints

```text
Off-limits: external sends, publication, paid commitments, sensitive data, destructive changes without approval
Allowed tools: local files, Codex, available project tools
```

## Human Approval Needed For

```text
external-facing, sensitive, paid, legal, financial, housing, medical, safety, memory, or destructive actions
```

## Definition Of Done

```text
A usable first-run project packet exists, source evidence is indexed, workstreams are routed, approval boundaries are explicit, and the next step is obvious.
```

## First Diagnostic Question

```text
Are totals and percentages calculated before the AI sees the data, or is the AI calculating them itself?
```

## Immediate Unknowns

```text
Actual current pipeline implementation.
Current source schemas from PDFs, Legal Tracker, and TeamConnect.
Whether calculations occur in prompt layer, code, SQL, spreadsheet logic, or another rules layer.
Existing report template requirements.
Accepted tolerance and reconciliation rules for financial metrics.
Data sensitivity and permission boundaries for any sample files.
```
