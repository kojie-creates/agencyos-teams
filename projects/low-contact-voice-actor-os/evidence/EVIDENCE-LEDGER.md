# Evidence Ledger

## Purpose

Track proof for claims, buyer research, outreach approvals, responses, recordings, pricing, and closeout.

## Ledger

| Evidence ID | Date | Workstream | Artifact | Status | Notes |
| --- | --- | --- | --- | --- | --- |
| E-001 | TBD | project-charter | `LOW-CONTACT-VOICE-ACTOR-OS.md` | created | Operating design artifact only |
| E-002 | TBD | intake | `intake.md` | created | Actor answers pending |
| E-003 | TBD | positioning | `positioning/CLAIM-AUDIT.md` | created | Claims pending evidence |
| E-004 | TBD | market-intel | `market-intel/LEAD-TRACKER.csv` | created | Shell rows only |
| E-005 | TBD | outreach | `outreach/OUTREACH-BATCH-001.md` | drafted_not_sent | Requires approval before use |
| E-006 | TBD | pipeline | `pipeline/PIPELINE-FIELDS.md` | created | Tracker rules defined |
| E-007 | 2026-09-05 | intake | Actor answers in chat | pending_claim_review | Email, Backstage link, paid project, no accolades, descriptors, studio setup, and quote rule supplied |
| E-008 | 2026-09-05 | positioning | `https://www.backstage.com/vo/kojie-montanez/` | reviewed | URL opened; content access limited |
| E-009 | 2026-09-05 | positioning | Audible search | pending_claim_review | Search did not verify audiobook pages; direct Audible URLs needed before external use |

## Intake Update Evidence

- Actor supplied (310) 422-6416 for buyer contact in the follow-up intake response.
- Actor explicitly restricted the October 2023 project to private proof and reported uncertainty about signing an NDA. This records an actor statement, not verified documentary proof or confirmed NDA status.
- Actor supplied https://open.spotify.com/show/2hfjJ9BQJLTVjpjt4yglbY. Opening this URL returned the title "Using Artificial Intelligence to grow Cannabis From Seed to Harvest: Cultivate cannabis with AI, no green thumb required !" and the label "Audiobook on Spotify". Accessible content did not establish narrator attribution, Audible availability, or The Creative Operating System credit.
- Actor supplied a 24-hour turnaround after receipt of scope, dependent on project size. Drafts qualify this as typical for smaller projects and confirm timing after scope review. No measured delivery average is established.
- Outreach remains drafted and unsent.

## Evidence Status Values

- `created`
- `drafted_not_sent`
- `pending_actor_input`
- `pending_claim_review`
- `approved`
- `sent`
- `response_logged`
- `recording_requested`
- `delivered`
- `closed`
- `rejected`

## Claim Evidence Rules

- Paid-project claims require a source, private proof, public credit, invoice, reference, or actor approval note.
- Accolades require exact wording and source.
- Studio claims require verified equipment and recording environment.
- Turnaround claims require actor availability approval.
- AI/TTS/model-training rights require separate written terms.

## Outreach Evidence Rules

- Store each outbound draft before approval.
- Store actor approval before sending.
- Store sent date only after actual send evidence exists.
- Store replies as summaries unless full text is needed.
- Mark all unsent drafts as `drafted_not_sent`.

## Current Evidence Boundary

The project has researched prospects, tailored drafts, and a single approval packet. No sent outreach, connected accounts, or live automation is established.
## Execution Evidence: 2026-09-05

- E-010: market-intel/BUYER-RESEARCH-001.md records official service and contact sources; demand unknown.
- E-011: evidence/SAMPLE-ACCESS-CHECK.md records browser access, public restricted-credit disclosure, and reachable direct media; playback unconfirmed. Supersedes earlier limited-access notes.
- E-012: outreach/OUTREACH-BATCH-001.md revision BATCH-001-v1 contains personalized unsent drafts. decisions/APPROVAL-PACKET-001.md centralizes the pending decision and sample hold.
- E-013: pipeline/PIPELINE-FIELDS.md separates drafting from successful sends and defines suppression and approval invalidation.
- Creation rows above are historical snapshots. Backstage now visibly self-reports narrator credits and Felix/Kojie identity; independent publisher verification remains absent.

## Clearance And Approval: 2026-09-05

- E-014: evidence/SAMPLE-ACCESS-CHECK.md records complete remote decode and local ASR content review; restricted project references not detected. Technical/transcript clearance only; subjective audio quality and universal browser compatibility unassessed.
- E-015: decisions/APPROVAL-PACKET-001.md records actor instruction to clear then approve; BATCH-001-v2 approved for initial emails only. Corrected numeric subjects and malformed tracker scores before finalization; v1 retained in evidence/OUTREACH-BATCH-001-v1-ARCHIVE.md.
- E-016: tracker rows now approved_to_send with sample_status cleared and approval reference populated. No actual send or follow-up dates recorded. Follow-ups remain separately unapproved.

## Hotmail Execution: 2026-09-05

- E-017: Outlook get_profile confirmed felix.montanez@hotmail.com. Approved batch SHA-256 matched 84B4F309B8FF4C8EF72DC10DFCD42DBC3E5EFF08E57763F57936E9556C7AB462. Complete Sent Items preflight returned six items, no matching recipients/messages, and no further page. Domain mailbox search returned no matches. Current actor prompt explicitly authorized exact initial sends.
- E-018: evidence/OUTLOOK-SEND-001.json records successful send tool responses and four matching Sent Items identifiers. Exact approved subjects, recipients and bodies were supplied; retrieved bodies match after whitespace normalization. Sent does not establish recipient delivery. pipeline/CONTACT-EVENTS.jsonl records each event and timestamp provenance.
- E-019: Loyal Studios subsequently bounced: recipient rejected, 550 5.4.1. evidence/BOUNCE-001.json records notification and original message identifiers. Tracker suppresses this address as do_not_contact pending correction; no follow-up dates. No retry authorized for a changed recipient.
- E-020: Ripe Media, Rip Media Group, and Lemonlight remain sent, with recipient delivery unconfirmed. Tracker records first follow-up due 2026-09-10 and final due 2026-09-16, from observed successful send completion dates in America/Los_Angeles. Weekends and Labor Day excluded using https://www.opm.gov/policy-data-oversight/pay-leave/federal-holidays/. Follow-ups require separate approval and were not sent. Dates are tracker entries only; no recurring automation established.
- Earlier unsent/account-unverified statements are historical snapshots superseded by this section. Approved draft file remains unchanged.

## Secondary lead source: 2026-09-06

- E-017: User attached `la_voiceover_leads_top100.xlsx` (100 ranked LA VO prospects). Filed as **secondary** under `market-intel/sources/`.
- Artifacts: `market-intel/sources/la_voiceover_leads_top100.xlsx`, `market-intel/sources/la_voiceover_leads_top100-SECONDARY.csv`, `market-intel/sources/SECONDARY-SOURCE-NOTE.md`.
- Overlaps with primary tracker (primary wins; do not re-contact from secondary): Ripe Media = LA-VO-007, Rip Media Group = LA-VO-008, Lemonlight = LA-VO-010.
- Operating rule: secondary informs research/draft queues only. `LEAD-TRACKER.csv` + approval packets remain send authority. Re-verify contacts before any new batch.

## Secondary CSV preferred: 2026-09-06

- E-018: User attached `la_voiceover_leads_top100.csv` — same 100 rows as the prior xlsx (100/100 name overlap). CSV is now the **preferred** secondary source.
- Artifacts updated under `market-intel/sources/`: raw CSV, enriched SECONDARY CSV, `NEXT-15-CANDIDATES.csv` (email-bearing, skips Batch 001 overlaps + podcast-intro/real-estate niches), updated `SECONDARY-SOURCE-NOTE.md`.
- Still secondary only. No sends. Primary tracker remains send authority.


## Batch 002 research and drafts: 2026-09-06

- E-019: market-intel/BUYER-RESEARCH-002.md records re-verification of NEXT-15 candidates (official sites, LA relevance, email page-confirmed vs secondary-only, fit scores).
- E-020: market-intel/LEAD-TRACKER.csv appended LA-VO-011 through LA-VO-025; Batch 001 rows LA-VO-007..010 unchanged. batch_id BATCH-002-v1; approval_ref decisions/APPROVAL-PACKET-002.md; sample_status cleared.
- E-021: outreach/OUTREACH-BATCH-002.md revision BATCH-002-v1 contains 12 personalized unsent drafts. Held: LA-VO-019, LA-VO-023. Pending verification not drafted: LA-VO-022.
- E-022: decisions/APPROVAL-PACKET-002.md centralizes PENDING actor approval; explicitly not sent; sample clearance references E-014/SAMPLE-ACCESS-CHECK; follow-ups not included.
- E-023: market-intel/sources/RESEARCH-LEADS-002-RESULT.md short ticket summary.


## Batch 002 send: 2026-09-06 (PT 2026-09-05 evening)

- E-024: decisions/APPROVAL-PACKET-002.md human gate APPROVE all 12; send authorized through Outlook / felix.montanez@hotmail.com.
- E-025: evidence/OUTLOOK-SEND-002.json — Graph send_mail status 202 for 12/12; Sent Items confirmation with message IDs and internetMessageIds; subjects/recipients match BATCH-002-v1. Recipient delivery not established.
- E-026: market-intel/LEAD-TRACKER.csv — LA-VO-011..018, 020, 021, 024, 025 status=sent; last_touch ~2026-09-05 11:35 PM PT; next_touch 2026-09-11; send_evidence refs OUTLOOK-SEND-002. Held/pending rows unchanged (019, 022, 023).
- E-027: pipeline/CONTACT-EVENTS.jsonl — SEND-002-* initial_sent events appended for all 12.
- Follow-ups: not approved; separate gate required.


## Follow-up approval: 2026-09-05 late PT

- E-028: Actor approved follow-ups for all successfully sent Batch 001 + Batch 002 leads; explicitly skipped Loyal bounce-fix and Sanchez re-verify.
- E-029: outreach/OUTREACH-FOLLOWUP-001.md revision FOLLOWUP-001-v1 — FU1/FU2 templates and 15-lead send list; due 2026-09-10 and 2026-09-16.
- E-030: decisions/APPROVAL-PACKET-FOLLOWUP-001.md stamped APPROVE; send on due dates only (not early).
- E-031: tracker rows for those 15 set status=follow_up_due, next_touch=2026-09-10, approval_ref FOLLOWUP packet.

## Calendar follow-up automation: 2026-09-05 late PT

- E-032: Outlook Calendar connector connected for felix.montanez@hotmail.com.
- E-033: Preflight found zero existing VO follow-up calendar events Sep 5–20; Sent Items confirmed 15 eligible initial sends.
- E-034: evidence/OUTLOOK-CALENDAR-FOLLOWUP-001.json — created FU1 2026-09-10 9–10am PT and FU2 2026-09-16 9–10am PT with default 15-minute reminders.
- E-035: Standing weekday 9am PT routine `vo-follow-up-calendar-sync` checks reminders + Sent Items and places missing follow-up calendar blocks. Blind auto-send FU1/FU2 routines removed.

## Daily drip standing approval: 2026-09-05 late PT

- E-036: Actor selected 10 per weekday with standing approve + auto-send for remaining secondary VO leads.
- E-037: decisions/STANDING-APPROVAL-DAILY-DRIP-v1.md and pipeline/DAILY-DRIP-OPS.md filed. First automated run 2026-09-08 weekday morning.
