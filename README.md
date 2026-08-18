# AgencyOS Teams

AgencyOS Teams is the plural flagship surface:

```text
AgencyOS Teams = AgencyOS Beings + AgencyOS Pro
```

It is for one human owner or organization working with multiple trusted AI teammates across parallel work lanes.

## What Is In This Folder

| Folder | Purpose |
| --- | --- |
| `base/` | Shared Being anatomy used across Core and Custom instances. |
| `agencyos-being-core/` | The reusable Being anatomy and template system. |
| `agencyos-being-custom/` | Installed/custom Being instances, personalities, skills, memory, and marketing assets. |
| `agencyos-pro/` | The multi-agency routing, governance, handoff, and closeout operating layer. |
| `beings/` | Teams-level roster for named AI Beings, roles, and collaboration boundaries. |
| `projects/` | Multiple complex projects, each with its own workstreams, deliverables, evidence, and closeout. |
| `workstreams/` | Separate work lanes that can run in parallel when safe. |
| `handoffs/` | Records of work moving between Beings, agencies, and workstreams. |
| `governance/` | Shared trust, approval, evidence, and permission rules for the whole team. |
| `docs/` | Product and marketing reference material. |
| `assets/` | Visual references for product relationship and work flow. |

## Activation Map

Read this first when starting work:

```text
ACTIVATION-MAP.md
```

## First Run

Use this to initialize a new AgencyOS Teams installation or project:

```text
FIRST-RUN.md
python tools/first_run.py
```

## Default Run Contract

When work starts inside this folder, AgencyOS Teams assumes the full local operating surface is available unless the user narrows scope.

Read:

```text
DEFAULT-RUN-CONTRACT.md
```

The user should not need to say:

```text
Use everything at your disposal.
```

That is already the folder contract.

## Named Being Rule

AgencyOS Teams does not use anonymous Beings.

Every generated or user-created Being must be named before it can be installed, routed, assigned to a workstream, referenced in a handoff, or used in closeout.

Read:

```text
CREATE-BEING-CONTRACT.md
```

## How To Think About It

AgencyOS Beings give the user:

```text
identity
presence
personality
memory
trusted working relationships
```

AgencyOS Pro gives the work:

```text
intake
classification
routing
parallel agencies
governance gates
evidence
closeout
learning
```

Together:

```text
Beings give Teams trusted collaborators.
Pro gives Teams coordinated execution.
```

## Shared Base Layer

The `base/` folder holds anatomy shared by Being Core and Being Custom.

Use it as the common reference for:

```text
body
history
intelligence
memory
personal
portfolio
presence
skeleton
sources
boundaries
evolution rules
installation rules
```

## Best Use

Use AgencyOS Teams when the work has:

```text
multiple complex projects
multiple work lanes
multiple AI teammates
parallel execution
shared governance
cross-lane learning
handoffs between agencies
one final human authority
```

AgencyOS Teams is the better fit when the request is too broad for a single focused workflow or when multiple complex projects need to stay organized separately.

## Canonical Requests

The safest default prompts for a local LM Studio + AgencyOS Teams setup are internal, low-risk, bounded, and artifact-producing. These are the top five default canon requests shipped in the repo:

```text
examples/canon-requests.json
```

1. `canon-local-proof` — local model proof packet
2. `canon-brief-synthesis` — internal brief synthesis
3. `canon-meeting-recap` — meeting recap and action items
4. `canon-decision-memo` — internal recommendation memo
5. `canon-runbook` — local setup runbook

These are designed to validate orchestration, artifact generation, review, and closeout without crossing external, financial, legal, or irreversible boundaries.

## Suggested Start

Use this folder when you want multiple named Beings to coordinate through AgencyOS Pro.

Example command shape:

```text
@operator Route this through AgencyOS Teams using the right AI Beings and Pro agencies.
```

Example:

```text
@operator Help Juan move FluidLogic into the elite athlete market using AgencyOS Teams.
```

Manual activation path:

```text
1. Start with agencyos-pro/getting-started-operator.md.
2. Select the needed Being personalities from agencyos-being-custom/personalities/.
3. Assign Beings through beings/.
4. Select or create the project folder under projects/.
5. Select or create the workstream folder under that project.
6. Route work through agencyos-pro/operator/ and agencyos-pro/agencies/.
7. Track handoffs under handoffs/ or the project handoff log.
8. Apply shared governance before any external-facing output.
9. Close with evidence, deliverables, and learning notes.
```

Project template:

```text
projects/_template/
```

Workstream template:

```text
workstreams/_template/
```

Handoff template:

```text
handoffs/HANDOFF-TEMPLATE.md
```

Governance standard:

```text
governance/GOVERNANCE-STANDARD.md
```

## Closeout Rule

Generated text is not completion.

AgencyOS Teams should close work only when:

```text
the artifact exists
the handoffs are traceable
the claim is supported
the governance boundary is respected
the human approval point is clear
the output is usable
the learning loop has somewhere to land
```

## Flagship Product Language

```text
AgencyOS Teams
Trusted AI teams for coordinated work.
```

Teams for scale.

## Marketing Assets

```text
docs/agencyos-teams-marketing.md
assets/agencyos-teams-operating-surface-graphic.svg
```
