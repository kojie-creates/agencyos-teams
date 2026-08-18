# Dev-Team Diagnostic Memo

Audience:

```text
Development team
```

Status:

```text
Approved by Kojie for dev-team-facing diagnostic use. Sending still requires explicit delivery instruction.
```

## Purpose

This memo turns the Diana spend reporting assistant evidence into a focused technical diagnostic path.

The goal is to confirm where the current pipeline is reliable, where it is ambiguous, and which processing steps must be deterministic before AI-generated text is produced.

## Current Understanding

Based on the customer briefs and diagnostic intake, the work supports legal spend management for a legal spend department.

The workflow appears to begin with collecting legal spend data, processing it, and producing summaries plus plans of action for improvement.

Current inputs are described as CSV files sent to an Azure-based system, after which reports are produced.

The source input should be treated as correct when source data and generated output disagree. The working assumption is that errors are being introduced by the system output layer or processing pipeline, not by the original input files.

Evidence status:

```text
Customer problem: supported.
Azure system: supported by diagnostic response, implementation details unknown.
Actual processing architecture: unknown.
Root cause: not implementation-verified.
```

## Diagnostic Priority

The first question to answer is:

```text
Where exactly does raw CSV data become verified output data?
```

The system should be inspected as a pipeline, not as one AI prompt.

Recommended pipeline map:

```text
CSV input
-> schema validation
-> data normalization
-> deterministic processing
-> validation and reconciliation
-> approved source-of-truth dataset
-> AI-assisted summary or recommendation draft
-> human review
-> PDF / spreadsheet / graph output
```

## Questions For The Dev Team

### 1. Input Handling

```text
What CSV files does the Azure system receive?
What columns, field types, and required values are expected?
What rejects or flags malformed, missing, duplicated, or inconsistent rows?
Are source files preserved unchanged for audit and comparison?
```

### 2. Source Of Truth

```text
When generated output disagrees with source CSV data, which object is treated as authoritative?
Is there a preserved clean dataset after processing?
Can every generated claim trace back to source rows or approved derived fields?
```

### 3. Deterministic Processing

```text
Which legal spend processing steps are handled by code, formulas, SQL, rules, or another deterministic method?
Which steps, if any, are handled inside an AI prompt?
Are summaries and plans of action generated only after deterministic processing is complete?
```

### 4. Validation And Reconciliation

```text
What system truth checks run before a human reviews the output?
What compares generated outputs against source data?
What errors block output generation?
What errors create escalation instead of allowing the system to proceed?
```

### 5. AI Boundary

```text
What is AI allowed to draft, summarize, classify, or recommend?
What is AI forbidden from deciding?
If an error occurs, does the system stop and escalate rather than updating the process or output?
```

### 6. Output Generation

```text
How are PDF documents generated?
How are spreadsheets and graphs generated?
Are output templates controlled separately from AI-generated text?
What checks ensure format consistency across reports?
```

### 7. Human Approval

```text
Who approves final output?
Which outputs are public-facing?
Which outputs may include proprietary data?
What evidence must be attached before public-facing or proprietary-data-risk output is approved?
```

## Recommended Technical Standard

The AI layer should not be the authority for processing legal spend data.

Recommended boundary:

```text
Deterministic system:
- validate inputs
- normalize data
- process legal spend data
- reconcile generated values against source data
- produce a verified reference dataset

AI layer:
- draft summaries
- explain verified patterns
- suggest possible plans of action
- prepare narrative for human review

Human reviewer:
- approve output
- approve public-facing use
- approve proprietary-data-risk output
- decide escalation when errors occur
```

## Evidence Needed Before Implementation Claims

To move from hypothesis to verified implementation facts, request:

```text
sample redacted CSV input
CSV schema or data dictionary
pipeline diagram or code path
prompt templates, if AI is used
validation rule list
example generated PDF
example generated spreadsheet or graph
known failing example
expected correct output for that example
error and escalation behavior
approval workflow
```

## Suggested First Fix Area

Start with the CSV-to-verified-dataset boundary.

Reason:

```text
If the source input is assumed correct, the system needs a deterministic checkpoint before any AI-generated output. Without that checkpoint, it is difficult to distinguish source issues, processing errors, AI narrative drift, and formatting defects.
```

## Non-Goals

```text
Do not ask AI to repair source data without explicit rules.
Do not let AI update the process when an error occurs.
Do not treat generated reports as approved without human review.
Do not send public-facing or proprietary-data-risk output without approval.
Do not claim the actual root cause is confirmed until implementation evidence is reviewed.
```

## Next Action

Ask the dev team to provide the pipeline map and one redacted end-to-end example:

```text
source CSV
expected processed data
generated output
known correction or discrepancy
validation/error behavior
```

That evidence will allow the next memo to move from diagnostic questions to a concrete remediation plan.
