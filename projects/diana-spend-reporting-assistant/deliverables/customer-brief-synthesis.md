# Customer Brief Synthesis

Audience:

```text
Internal AgencyOS Teams first-run.
```

## Source-Bound Summary

The customer briefs describe an automated spend reporting assistant that generates analysis, observations, cost-saving recommendations, and client-ready report text.

The reported problem is not that Diana dislikes the analysis work. The key requirement is that the calculations must be correct before Diana interprets the spend and advises clients.

The briefs identify a likely architecture issue: the current workflow appears to ask the AI layer to interpret messy data, calculate financial metrics, generate analysis, and write narrative. That is risky for financial reporting because language models are not deterministic calculation engines.

## Evidence Status

| Claim | Status |
| --- | --- |
| Reports frequently require manual correction. | supported |
| Errors include numerical interpretation, totals, formatting, and narrative/data mismatch. | supported |
| The system likely uses Azure OpenAI. | inferred |
| The AI may be calculating financial metrics inside the prompt layer. | inferred |
| The actual production pipeline is confirmed. | unknown |
| Separating deterministic calculations from narrative generation is the recommended design direction. | supported |

## Customer Requirement

```text
Support Diana's analysis. Do not replace it.
```

Automation should own:

```text
data preparation
calculation accuracy
formatting consistency
validated metrics
draft narrative generation after verification
```

Diana should own:

```text
spend interpretation
client advice
final judgment
approval of report language
approval of client-facing output
```

## Target Architecture

```text
PDF / Legal Tracker / TeamConnect
-> extraction layer
-> normalization layer
-> deterministic calculation layer
-> validation and reconciliation
-> verified spend metrics
-> report template
-> AI narrative and observations
-> Diana review and approval
```

## Dev-Team Diagnostic Questions

```text
Are totals and percentages calculated before the AI sees the data, or is the AI calculating them itself?
Where do extracted PDF tables become structured data?
What schema normalizes PDF, Legal Tracker, and TeamConnect inputs?
Which deterministic layer computes totals, percentages, trends, and cost metrics?
What validation checks reconcile generated report numbers against source data?
Can the AI narrative reference only verified metrics?
Is report formatting template-driven or generated directly by the model?
What test cases currently catch numeric drift?
```

## Recommended Workstreams

```text
source-synthesis
technical-diagnostic
executive-alignment
implementation-path
```

## Risk Notes

```text
Do not present likely root cause as verified implementation fact.
Do not make financial outcome claims.
Do not process sensitive client spend data without approval.
Do not send external messaging without human approval.
```
