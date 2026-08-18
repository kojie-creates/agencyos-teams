# User Decision Menu

Purpose:

```text
After first-run, present clear next-step choices to the user before preparing external artifacts.
```

## Recommended Next Decision

```text
Choose the first audience packet to prepare.
```

Default recommendation:

```text
Prepare the dev-team diagnostic memo first.
```

Why:

```text
The customer problem points to a likely architecture issue, but the actual implementation is still unknown. A dev-team diagnostic memo can confirm where calculations happen before any executive or customer-facing claim is sharpened.
```

## External Artifact Options

| Option | Artifact | Audience | Purpose | Approval Needed Before Send |
| --- | --- | --- | --- | --- |
| A | Dev-team diagnostic memo | Development team | Ask the right pipeline questions and confirm calculation ownership. Intake script available at tools/dev_team_diagnostic_intake.py. | Yes |
| B | Diana-facing summary | Diana | Acknowledge the problem and explain the support-not-replace design direction. | Yes |
| C | Executive summary | Executive stakeholders | Frame the issue as architecture, impact, and recovery path. | Yes |
| D | Data/request checklist | Diana or dev team | Ask for schemas, templates, redacted samples, and validation rules. | Yes |
| E | Implementation recovery plan | Internal or dev team | Sequence extraction, normalization, deterministic metrics, validation, templates, and AI narrative. | Yes |

## Internal Artifact Options

| Option | Artifact | Audience | Purpose |
| --- | --- | --- | --- |
| F | Source-bound briefing note | Kojie | Preserve what the PDFs support and what remains unknown. |
| G | AgencyOS routing map | Kojie | Show which Beings and workstreams own each lane. |
| H | Risk and claims review | Kojie | Prevent overclaiming before external communication. |

## Decision Prompt To Show User

```text
First-run is complete. Which next artifact should I prepare first?

Recommended: A. Dev-team diagnostic memo.

To collect dev-team answers first, run:

python tools/dev_team_diagnostic_intake.py

For this Diana project, run the generic diagnostic with Diana's data as the named use case:

python tools/dev_team_diagnostic_intake.py --use-case diana-spend-reporting-assistant

Other options:
B. Diana-facing summary.
C. Executive summary.
D. Data/request checklist.
E. Implementation recovery plan.
F. Internal source-bound briefing note.
G. AgencyOS routing map.
H. Risk and claims review.
```

## Rule

```text
Do not prepare or send external-facing artifacts until the user chooses the audience and approves the direction.
```

## Intake Script

```text
python tools/dev_team_diagnostic_intake.py
```

For first-run requests that mention a dev-team diagnostic lane for the user and work involved, first-run now starts this intake automatically after the packet is created.

Diana's information lives under:

```text
--use-case diana-spend-reporting-assistant
```

The script asks each diagnostic question, lets the user attach upload paths, copies uploads into evidence/dev-team-diagnostic-uploads, and writes:

```text
evidence/dev-team-diagnostic-responses.md
evidence/dev-team-diagnostic-responses.json
```
