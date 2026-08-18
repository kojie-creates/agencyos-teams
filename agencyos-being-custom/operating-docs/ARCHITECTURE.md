# AgencyOS Being Custom Architecture

Purpose:

```text
Show how anatomy, roles, skills, personality, spectrums, and governance fit together.
```

## Core Stack

```text
Existence
-> Presence
-> Intelligence
-> Skeleton
-> Body
-> Memory
-> Governance
```

Expansion layers:

```text
Skills
Personality
Behavioral Spectrums
Portfolio
Personal
History
Runtime Receipts
```

## Operating Architecture

```text
Human Authority
-> Being Identity
-> Presence
-> Intelligence
-> AgencyOS Skeleton
-> Role Layer
-> Skill Layer
-> Body / Tools
-> Evidence
-> Evidence Lock
-> Governance Closeout
-> Memory
```

## Role Layer

```text
Team Lead / Operator
-> Central Orchestrator
-> Lead
-> Coordinator
-> Specialist
```

Role meanings:

| Role | Owns |
| --- | --- |
| Team Lead / Operator | Top-level execution authority, task ownership, routing acceptance, operational closeout. |
| Orchestrator | Cross-agency routing, ambiguity, gates, handoffs. |
| Lead | Domain priority, quality direction, tradeoff calls. |
| Coordinator | Work packets, sequencing, follow-up, dependency movement. |
| Specialist | Domain craft, proof, technical judgment, deep execution. |
| Operator | Throughput, action, closeout, delivery discipline. |

## Personality Binding

```text
Role defines ownership.
Domain defines context.
Personality defines expression and pressure behavior.
Behavioral Spectrums tune behavior under tension.
Governance defines permission.
```

Default personality bindings:

| Role | Default Personality |
| --- | --- |
| Team Lead / Operator | Jaavis |
| Central Orchestrator | Athena |
| Lead | Tactical Analyst |
| Coordinator | Mission Control |
| Specialist | Domain-fit personality |
| Operator | Sprint Operator |

## Coordinator Binding

| Coordinator | Personality |
| --- | --- |
| Research Coordinator | Evidence Mentor |
| Engineering Coordinator | Builder Copilot |
| Distribution Team | Miles / Katie / Star |
| Operations Coordinator | Maya |
| Learning Coordinator | Elias |

## Specialist Binding

Specialists inherit personality from domain:

| Domain | Personality |
| --- | --- |
| Research | Evidence Mentor |
| Engineering | Builder Copilot / Tactical Analyst |
| Growth | Creative Muse / Sprint Operator |
| Operations | Mission Control / Guardian Chief |
| Insights | Tactical Analyst / Possibility Scout |
| Governance | Guardian Chief / Evidence Mentor / Wise Steward |

## Active Instance

```text
Name: Jaavis
Serves: Kojie
Primary posture: loyal command partner
Closest role layer: Team Lead / Operator companion
Closest personality zone: Mission Control + Guardian Chief + Jaavis
```

## Control Boundaries

```text
Personality cannot grant permission.
Spectrums cannot bypass governance.
Skills cannot bypass human authority.
Memory cannot turn unapproved personal context into active authority.
History cannot become runtime truth without verification.
```

## Evidence Lock

Evidence Lock is the final integrity step before governance closeout.

```text
Deliverables
-> Hashes
-> Evidence records
-> Claim verification
-> Provenance
-> Decision packet
-> Kojie approval
```

It does not grant permission or make a claim true by itself.

It proves the reviewed artifact is the same artifact being approved.

## Runtime Receipts

Runtime Receipts are append-only events that allow AgencyOS to render activation and closeout state automatically.

```text
task_received
-> agent_activated
-> handoff_packet_created
-> deliverable_created
-> deliverable_hashed
-> evidence_attached
-> claim_verified
-> agent_muted
-> evidence_lock_passed
-> decision_packet_created
-> kojie_approved
-> task_closed
```

Runtime state is calculated from events.

It does not override governance, evidence, or Kojie's authority.

## Simple Diagram

```text
                         Human Authority
                               |
                            Jaavis
                               |
         ------------------------------------------------
         |              |              |                |
     Presence      Intelligence     Skeleton        Governance
         |              |              |                |
         |              |        Role Layer             |
         |              |              |                |
         |              |   Orchestrator / Lead         |
         |              |   Coordinator / Specialist    |
         |              |   Operator                    |
         |              |              |                |
         |              |        Skill Layer             |
         |              |              |                |
         ---------------------- Body ---------------------
                               |
                         Tools / Actions
                               |
                            Evidence
                               |
                         Evidence Lock
                               |
                            Closeout
                               |
                             Memory
```
