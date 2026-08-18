# Seed Data Example: Independent Fitness Studio

Use case:

```text
Independent fitness studio using AgencyOS Pro for 90 days.
```

Assumption:

```text
The studio showed up consistently, logged daily work, used agencies for member acquisition, class operations, retention, content, risk, and improvement.
```

## Agencies

| Agency | Config | Owns |
|---|---|---|
| Member Growth | Studio | offers, local content, referral campaigns |
| Class Operations | Assembly Line | class prep, attendance, coach notes, daily closeout |
| Member Retention | Pod | at-risk members, follow-ups, renewal nudges |
| Risk + Proof | Governance | waiver reminders, health claims, safety checks |
| Insights | Continuous Improvement | attendance trends, campaign learning, churn signals |

## Queue Snapshot

| ID | Agency | Config | Task | Owner | Status | Risk | Follow-up |
|---|---|---|---|---|---|---|---|
| FIT-001 | Member Growth | Studio | Create 4-week beginner strength campaign | Growth Coordinator | closed | medium | monitor |
| FIT-002 | Class Operations | Assembly Line | Build daily class closeout checklist | Operations Coordinator | closed | low | template |
| FIT-003 | Member Retention | Pod | Identify members missing 2+ weeks | Insights Coordinator | active | medium | weekly monitor |
| FIT-004 | Risk + Proof | Governance | Review "fat loss" ad language | Risk Assessment | closed | high | periodic review |
| FIT-005 | Insights | Continuous Improvement | Compare 30-day attendance before/after campaign | Analytics | active | low | monthly review |

## Decision Log

| Date | Decision | Owner | Evidence | Revisit |
|---|---|---|---|---|
| 2026-06-15 | Replace "rapid fat loss" claim with "build consistent strength habits" | Studio Owner | Risk review and ad draft | monthly |
| 2026-06-28 | Convert class closeout checklist into reusable template | Operations Coordinator | 18 completed closeouts | quarterly |
| 2026-07-05 | Prioritize beginner members over advanced athletes for next campaign | Strategy Advisor | attendance and inquiry themes | after next campaign |

## Evidence Ledger

| Claim | Source | Artifact | Owner | Status | Last Checked |
|---|---|---|---|---|---|
| Beginner strength campaign increased intro-class bookings | booking log | campaign-report-june.md | Analytics | supported | 2026-07-01 |
| Studio offers beginner-friendly coaching | class schedule, coach notes | beginner-offer-page.md | Risk + Proof | supported | 2026-07-03 |
| "Rapid fat loss" claim | draft ad | ad-claim-review.md | Risk Assessment | rejected | 2026-06-15 |

## Memory Snapshot

Private memory:

```text
Member Growth:
- Best performing hook: "start strength training without feeling lost"
- Weak hook: "summer shred"
- Strong channel: local Facebook groups

Class Operations:
- Coaches forget post-class notes unless checklist is under 5 fields.
- Late cancellations spike on Mondays.

Member Retention:
- Members who miss 2 weeks often respond to personal check-ins.
- New members need first-14-day support.
```

Shared memory:

```text
Approved offer language:
"Build consistent strength habits with coach-led small group training."

Rejected language:
"Rapid fat loss"
"Guaranteed body transformation"

Current priority:
Increase beginner intro-class attendance and reduce early churn.
```

## Daily Log Samples

| Date | Signal | Agency | Note | Action |
|---|---|---|---|---|
| 2026-06-10 | 3 new inquiries from Facebook post | Member Growth | beginner angle working | create 2 follow-up posts |
| 2026-06-12 | 5 members missed second class | Member Retention | early churn risk | send check-in template |
| 2026-06-18 | coach notes incomplete | Class Operations | checklist too long | reduce fields |
| 2026-06-21 | ad draft used aggressive health claim | Risk + Proof | claim too strong | revise language |
| 2026-07-01 | intro class bookings up | Insights | campaign likely helping | compare next 30 days |

## Retrospective Snapshot

What worked:

```text
Beginner-focused messaging produced clearer inquiries.
Short coach closeout checklist improved consistency.
Personal check-ins helped recover inactive members.
```

What broke:

```text
Ad copy drifted into unsupported health claims.
Operations checklist was too long at first.
Retention follow-up needed a weekly owner.
```

What changed:

```text
Risk + Proof now reviews all public health/fitness claims.
Class closeout checklist became a template.
At-risk member list is reviewed every Monday.
```

Closeout labels:

```text
beginner campaign: monitor
class closeout checklist: template
health claim policy: periodic review
at-risk member follow-up: monitor
```
