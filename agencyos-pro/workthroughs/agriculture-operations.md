# Walkthrough: Agriculture Operations

Industry:

```text
Specialty crop farm with field operations, labor planning, buyers, compliance, equipment, and harvest windows.
```

Primary failure modes:

```text
Chaotic intake
No clear owner
Big deadline
Risk visibility
Stale field knowledge
```

Agencies:

```text
Field Operations AgencyOS
Buyer and Sales AgencyOS
Compliance and Risk AgencyOS
Insights AgencyOS
```

Configs:

```text
Field Operations: Pod Model by crop block or field.
Buyer and Sales: Studio Model for buyer updates, availability sheets, and outreach.
Compliance and Risk: Governance Overlay for pesticide logs, worker safety, water records, and certifications.
Insights: Continuous Improvement Loop for yield, labor, waste, buyer feedback, and timing.
```

Example request:

```text
@operator We are two weeks from harvest. Help coordinate labor, buyer updates, compliance checks, and risk review for three crop blocks.
```

Operator routing:

```text
Scope Gate: one harvest coordination project.
Risk Gate: high, because labor, buyer commitments, and compliance are involved.
Config Selector: Pod Model plus Swarm plus Governance Overlay.
Agency Selector: Field Operations owns harvest readiness. Buyer and Sales owns buyer communication. Compliance and Risk reviews required logs.
```

Expected outputs:

```text
harvest readiness checklist
field-by-field owner map
labor and equipment plan
buyer availability update
compliance evidence checklist
risk register
daily monitor cadence
post-harvest retrospective
```

Continuous improvement:

```text
After harvest, Insights reviews waste, labor gaps, buyer complaints, weather delays, equipment issues, and updates next-season templates.
```

