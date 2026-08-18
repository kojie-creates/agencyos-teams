# Seed Data Example: Performance Coach

Use case:

```text
Independent performance coach using AgencyOS Pro for 90 days.
```

Assumption:

```text
The coach logged sessions, client follow-ups, exercises, content drafts, outcome claims, testimonials, and weekly learning.
```

## Agencies

| Agency | Config | Owns |
|---|---|---|
| Client Pods | Pod | client-specific goals, session notes, follow-ups |
| Program Build | Assembly Line | exercises, frameworks, session structure, templates |
| Content Studio | Studio | posts, newsletters, short teaching assets |
| Opportunity | Growth Loop | discovery calls, referrals, offer language |
| Risk + Proof | Governance | outcome claims, testimonials, client boundaries |
| Insights | Continuous Improvement | feedback, completion rates, repeated blockers |

## Queue Snapshot

| ID | Agency | Config | Task | Owner | Status | Risk | Follow-up |
|---|---|---|---|---|---|---|---|
| PC-001 | Client Pods | Pod | Create 14-day follow-up plan for Client A | Operations Coordinator | closed | medium | monitor |
| PC-002 | Program Build | Assembly Line | Turn recurring focus exercise into reusable template | Engineering Coordinator | closed | low | template |
| PC-003 | Content Studio | Studio | Draft 5 posts from common client blockers | Growth Coordinator | active | medium | review |
| PC-004 | Risk + Proof | Governance | Review testimonial language before publishing | Risk Assessment | closed | high | proof gate |
| PC-005 | Insights | Continuous Improvement | Compare completion rates by exercise type | Analytics | active | low | monthly review |

## Decision Log

| Date | Decision | Owner | Evidence | Revisit |
|---|---|---|---|---|
| 2026-06-18 | Use "support consistency" instead of "guarantee performance gains" | Risk + Proof | claim review | monthly |
| 2026-06-25 | Make next actions smaller after each session | Strategy Advisor | client completion notes | 30 days |
| 2026-07-04 | Build offer around accountability and execution, not motivation | Opportunity | discovery call themes | next campaign |

## Evidence Ledger

| Claim | Source | Artifact | Owner | Status | Last Checked |
|---|---|---|---|---|---|
| Small next actions improved completion | session notes | completion-rate-review.md | Analytics | supported | 2026-07-10 |
| "Guaranteed performance gains" | draft sales page | claim-review.md | Risk Assessment | rejected | 2026-06-18 |
| Client testimonial approved for public use | client approval email | testimonial-log.md | Risk + Proof | supported | 2026-07-02 |

## Memory Snapshot

Private memory:

```text
Client Pods:
- Client A struggles when next action has more than 2 steps.
- Client B responds well to written recap within 24 hours.

Program Build:
- Best reusable artifact: weekly decision reset.
- Weak artifact: long reflection worksheet.

Content Studio:
- Strong content theme: "execution after clarity."
- Weak theme: generic motivation posts.
```

Shared memory:

```text
Approved positioning:
"Performance coaching for people who need structure, accountability, and clearer execution."

Rejected positioning:
"Guaranteed performance transformation"
"Unlock your full potential instantly"

Current priority:
Improve follow-through after sessions and turn repeated exercises into reusable assets.
```

## Daily Signal Samples

| Date | Signal | Agency | Note | Action |
|---|---|---|---|---|
| 2026-06-11 | Client missed assigned exercise | Client Pods | action was too broad | rewrite as 1-step task |
| 2026-06-17 | same blocker appeared in 3 sessions | Content Studio | useful post topic | draft teaching post |
| 2026-06-21 | testimonial draft overclaimed | Risk + Proof | claim too strong | revise and request approval |
| 2026-06-30 | high completion after recap email | Insights | recap likely useful | make recap template |
| 2026-07-08 | discovery calls mention accountability | Opportunity | offer language signal | update offer page |

## Retrospective Snapshot

What worked:

```text
Short next actions improved client follow-through.
Session recap emails reduced confusion.
Content based on real client blockers felt more specific.
```

What broke:

```text
Some testimonial language implied guaranteed outcomes.
Long exercises reduced completion.
Discovery calls lacked a consistent qualification script.
```

What changed:

```text
Risk + Proof reviews testimonials before publishing.
Program Build converted best exercises into templates.
Opportunity created a discovery script.
Insights monitors completion rates monthly.
```

Closeout labels:

```text
session recap template: template
testimonial approval workflow: proof gate
client follow-up plan: monitor
program exercises: periodic review
```
