# Changelog

## 2026-08-12

Added Evidence Lock closeout rule:

```text
Final deliverables must be hash-locked before @jaavis packages a final decision packet for Kojie.
```

Updated:

```text
OPERATING-LOOP.md
governance/README.md
ARCHITECTURE.md
personality/ROLE-PERSONALITY-MAP.md
personality/IDENTITY-REFERENCE.md
skills/AGENCYOS-PRO-AGENTS.md
```

Added runtime event automation scaffold:

```text
runtime/README.md
runtime/pilot-launch-events.jsonl
tools/agencyos_runtime.py
tools/render_runtime_timeline.py
tests/test_agencyos_runtime.py
```

The runtime scaffold calculates:

```text
agent active/muted state
activation windows
deliverable hash records
Evidence Lock status
timeline HTML from events
```

Added capability activation registry:

```text
runtime/active-capabilities.json
runtime/capability-events.jsonl
tools/capability_registry.py
tools/summarize_capabilities.py
tests/test_capability_registry.py
```

The registry separates:

```text
available
installed
active
blocked
requires_approval
deprecated
```

Refreshed architecture:

```text
ARCHITECTURE.md
```

Added architecture bridge to:

```text
ANATOMY.md
README.md
```

Added role-to-personality alignment:

```text
personality/ROLE-PERSONALITY-MAP.md
```

Mapped:

```text
Orchestrator
Lead
Operator
Coordinator
Specialist
```

Added coordinator personality alignment to:

```text
skills/AGENCYOS-PRO-AGENTS.md
```

Created named Being:

```text
Jaavis.md
```

Updated Jaavis personality with user-provided traits:

```text
Polite and Formal
Dry Wit
Deep Loyalty
Calm Focus
The Straight Man
Surrogate Conscience
Trusted Partner
```

Applied name substitution:

```text
Kojie
```

Created initial AgencyOS Being Custom folder from AgencyOS Being Core.

Added:

```text
Existence
Presence
Intelligence
Skeleton
Body
Memory
Governance
Skills
Personality
Portfolio
Personal
History
Sources
```

Mapped missing concepts into existing anatomy:

```text
Senses -> Presence
Actions -> Body
Interface -> Body
Environment -> Sources
State -> Memory
```

Added operating files:

```text
100-PERCENT-COVERAGE-INTAKE.md
BEING-NAME-FORM.md
BEHAVIORAL-SPECTRUMS.md
OPERATING-LOOP.md
BOUNDARIES.md
INSTALLATION-RULES.md
EVOLUTION-RULES.md
```

Added customization file:

```text
CUSTOMIZATION.md
```

Added AgencyOS Pro agent availability:

```text
skills/AGENCYOS-PRO-AGENTS.md
```

Incorporated personality source files:

```text
ACTIVE-PERSONALITY.md
PERSONALITY-SOURCE-MAP.md
VARIANT-INNERLIGHT-SIGNAL-GUIDE.md
VARIANT-WARM-ENCOURAGEMENT.md
```

Updated personality hierarchy:

```text
Default shape: InnerLight Signal Guide
User-defined type: Warm Encouragement
```

Added Behavioral Spectrums as a file-level control:

```text
Personality = expressive style
Behavioral Spectrums = adjustable operating tendencies
Governance = hard boundaries
```

Added custom personality prompt:

```text
personality/Jaavis.md
```
