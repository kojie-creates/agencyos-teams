# Walkthrough: Veterinary Clinic Operations

Industry:

```text
Veterinary clinic managing appointments, client communication, treatment plans, inventory, follow-ups, and staff coordination.
```

Primary failure modes:

```text
Chaotic intake
Skipped steps
Human workload bottleneck
Trust gaps
No learning loop
```

Agencies:

```text
Client Communication AgencyOS
Clinic Operations AgencyOS
Care Follow-Up AgencyOS
Risk and Compliance AgencyOS
```

Configs:

```text
Client Communication: Hub-and-Spoke for calls, emails, reminders, estimates, and follow-ups.
Clinic Operations: Assembly Line for appointment prep, visit flow, discharge, billing, and records.
Care Follow-Up: Pod Model by patient case or care plan.
Risk and Compliance: Governance Overlay for medical record completeness, consent, privacy, and controlled-substance handling.
```

Example request:

```text
@operator Help reduce missed follow-ups and improve communication for post-surgery patients.
```

Operator routing:

```text
Scope Gate: one clinic workflow improvement.
Risk Gate: critical if medical advice or patient safety is involved.
Config Selector: Assembly Line plus Pod Model plus Governance Overlay.
Agency Selector: Care Follow-Up owns patient outcomes. Client Communication owns messaging. Risk and Compliance reviews boundaries.
```

Expected outputs:

```text
post-surgery follow-up schedule
client message templates
red-flag escalation checklist
staff handoff packet
medical-record completeness checklist
monitoring log
monthly review cadence
```

Continuous improvement:

```text
Insights reviews missed callbacks, client confusion, staff burden, readmission patterns, and updates templates.
```

