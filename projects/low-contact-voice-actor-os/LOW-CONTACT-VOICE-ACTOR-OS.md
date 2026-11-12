# Low-Contact Voice Actor OS

## Project Charter

**Project Name:** Low-Contact Voice Actor OS

**Owner:** Felix Montanez

**Primary Operator:** AgencyOS Teams, with human approval gates

**Talent Profile:** Los Angeles, California voice actor with a conversational, warm, radio-style announcer voice, early paid-project experience, and no accolades currently approved for buyer-facing use.

**Goal:** Build a governed operating system that lets the voice actor spend as little time as possible on administration while still preserving human authority over public-facing claims, buyer contact, pricing, recording, and deal acceptance.

**Operating Principle:** AgencyOS Teams may automate preparation, drafting, routing, tracking, and review. No buyer-facing action is sent without explicit human approval.

## Outcome

Create a low-contact voice-over business workflow that can:

- Use approved voice descriptors and studio capabilities for honest positioning; keep restricted credits private.
- Research and rank Los Angeles voice-over buyers.
- Draft tailored outreach and follow-ups.
- Stage sample-read opportunities.
- Track buyer status, next action, response quality, and evidence.
- Prepare production checklists, quote inputs, and delivery packets.
- Produce weekly decision reports for the actor.

## Why This Needs AgencyOS Teams

This project has multiple work lanes that should move in parallel but stay governed:

- Market research needs buyer lists, fit notes, and verification status.
- Positioning needs claim review before anything public-facing is used.
- Outreach needs drafting, sequencing, and approval checkpoints.
- Pipeline operations need structured tracking and follow-up discipline.
- Production operations need clean handoffs from buyer request to recording, delivery, invoice, and closeout.
- Audit operations need an evidence trail for claims, buyer status, outreach approvals, and paid-work outcomes.

AgencyOS Teams is the shared operating framework for these lanes. AgencyOS One can later become the focused daily execution surface for one active workflow at a time.

## Human Contact Model

The actor should only be pulled in for high-value decisions:

| Contact Point | Actor Action | Gate |
| --- | --- | --- |
| Positioning approval | Approve profile, offer, and claim language | Required before outreach |
| Sample recording | Record selected scripts or auditions | Required for all audio |
| Outreach approval | Approve message batches before send | Required before buyer contact |
| Pricing approval | Approve quote range or final offer | Required before proposal |
| Buyer call | Attend serious calls only | Required for relationship handoff |
| Contract/payment approval | Approve SOW, license, invoice, or payment terms | Required before commitment |

## Automation Scope

AgencyOS Teams can automate or semi-automate:

- Lead discovery and enrichment.
- Buyer category mapping.
- Fit scoring and priority ranking.
- Outreach draft creation.
- Follow-up draft creation.
- CRM or tracker updates.
- Response classification.
- Weekly status summaries.
- Sample script suggestions.
- Quote-prep checklists.
- Delivery and closeout checklists.
- Evidence ledger updates.
- Claim and risk review before external use.

## Non-Automated Boundaries

These remain human-controlled:

- Sending messages from personal accounts unless the actor explicitly authorizes a specific batch.
- Claiming credentials, credits, clients, or accolades that are not evidenced.
- Recording or approving voice assets.
- Negotiating final usage rights, exclusivity, AI/TTS permissions, or buyouts.
- Accepting work.
- Signing contracts.
- Issuing final invoices.
- Representing the actor as available, committed, or legally bound.

## Workstream Design

### 1. Talent Positioning

**Purpose:** Convert raw talent facts into a clear, honest market-facing profile.

**Inputs:**

- Paid-project examples.
- Accolades.
- Backstage or demo links.
- Voice descriptors.
- Availability.
- Studio setup, if verified.

**Outputs:**

- Short bio.
- Buyer-facing one-liner.
- Voice descriptor bank.
- Approved claim list.
- Rejected or unverified claim list.

**Approval Gate:** Actor approves positioning before outreach.

### 2. Market Intelligence

**Purpose:** Build a Los Angeles buyer universe for a radio-style announcer voice.

**Buyer Categories:**

- Local production companies.
- Advertising and creative agencies.
- Podcast studios.
- Real estate media firms.
- Corporate video producers.
- E-learning producers.
- IVR and phone-system vendors.
- Local radio and streaming advertisers.
- Event and venue marketing teams.
- Startup product-video teams.

**Outputs:**

- Ranked lead tracker.
- Buyer category.
- Fit rationale.
- Contact method.
- Verification status.
- Outreach angle.

**Approval Gate:** Actor approves buyer category focus before outreach batches.

### 3. Outreach Operations

**Purpose:** Draft and stage low-friction outreach.

**Operating Rule:** Drafts may be prepared automatically. Sending requires human approval.

**Outputs:**

- Cold email drafts.
- LinkedIn drafts.
- Follow-up sequences.
- Short voicemail script.
- Buyer-specific personalization notes.
- Outreach batch approval sheet.

**Approval Gate:** Actor approves batch before send.

### 4. Pipeline Operations

**Purpose:** Reduce actor contact by keeping all follow-up state outside the actor's head.

**Fields To Track:**

- Buyer name.
- Category.
- Contact.
- Source.
- Fit score.
- Status.
- Last touch.
- Next touch.
- Response.
- Opportunity type.
- Required actor action.
- Evidence link.

**Approval Gate:** Actor only sees items requiring a decision or recording.

### 5. Production Operations

**Purpose:** Convert serious opportunities into clean recording and delivery tasks.

**Outputs:**

- Audition packet.
- Sample-read script.
- Recording checklist.
- File naming guide.
- Revision checklist.
- Delivery checklist.
- Quote-prep sheet.
- Invoice-prep sheet.

**Approval Gate:** Actor records, approves final audio, and approves final price/license terms.

### 6. Vera Audit And Claim Review

**Purpose:** Prevent inflated claims and risky automation.

**Checks:**

- Paid-project claims have evidence.
- Accolades are stated accurately.
- "Professional demo reel" is not used unless professionally produced.
- "Voice-over samples" or "sample reads" are used for early assets.
- AI/TTS or synthetic voice rights are not offered casually.
- Buyer-facing language does not imply commitment before approval.

**Approval Gate:** Any external-facing packet must pass claim review before use.

## Evidence Ledger

Each meaningful action should produce or update evidence:

- Source URL or contact source for each lead.
- Draft version for each outreach message.
- Human approval record for each sent batch.
- Response summary for each buyer reply.
- Recording request packet for each audition or paid job.
- Delivery confirmation for each completed project.
- Invoice and license note for each paid engagement.
- Weekly decision report.

Evidence can start as Markdown, CSV, or spreadsheet artifacts. Later productization may move it into a persistent runtime store.

## Minimal Actor Dashboard

The actor should receive a short decision report with only:

- Approvals needed.
- Recordings needed.
- Serious buyer replies.
- Recommended next focus.
- Risks or claims needing correction.
- Revenue or opportunity notes supported by evidence.

No full research dump unless requested.

## Initial Folder Plan

Recommended project structure:

```text
projects/low-contact-voice-actor-os/
  LOW-CONTACT-VOICE-ACTOR-OS.md
  intake.md
  positioning/
  market-intel/
  outreach/
  pipeline/
  production/
  evidence/
  decisions/
  closeout/
```

This packet is the first project artifact. The remaining folders and artifacts should be created as each workstream starts.

## First Execution Pass

### Pass 1: Intake And Claim Audit

Collect only the minimum needed from the actor:

- Name to use publicly.
- Preferred contact method.
- Existing demo or sample link.
- Paid-project evidence.
- Accolades to verify.
- Availability window.
- Studio capability, if any.
- Buyer categories to avoid.
- Price floor or "ask before quoting" rule.

### Pass 2: Positioning Draft

Create:

- One-line offer.
- Short bio.
- Three outreach angles.
- Approved voice descriptors.
- Claim-risk table.

### Pass 3: Market List

Create:

- A first Los Angeles buyer list.
- Fit scores.
- Contact sources.
- Suggested outreach angle per buyer.
- Verification status.

### Pass 4: Outreach Batch

Create:

- First outreach batch.
- Follow-up sequence.
- Human approval sheet.

No messages are sent until approval is recorded.

### Pass 5: Weekly Operating Review

Produce:

- What happened.
- What needs actor action.
- What can continue automatically.
- What claims or assumptions need correction.
- Next batch recommendation.

## Known Simulation Boundaries

This packet defines the operating design. It does not prove that:

- Lead research has been completed.
- Any messages have been sent.
- Any buyer has responded.
- Any CRM integration is live.
- Any email, calendar, or social account has been connected.
- Any payment or invoicing workflow is active.
- Any persistent runtime automation has been deployed.

Those claims require separate evidence.

## Next Technical Milestone

Updated 2026-09-05: scaffold artifacts exist. Buyer research and tailored drafts are staged in decisions/APPROVAL-PACKET-001.md. Next: clear sample playback/content and obtain batch approval. The creation list below is the completed scaffold milestone.

Create the first operational artifacts:

- `intake.md`
- `positioning/CLAIM-AUDIT.md`
- `market-intel/LEAD-TRACKER.csv`
- `outreach/OUTREACH-BATCH-001.md`
- `pipeline/PIPELINE-FIELDS.md`
- `evidence/EVIDENCE-LEDGER.md`

Milestone exit criteria:

- Actor approval gates are clearly marked.
- No buyer-facing claim is unsupported.
- Outreach is drafted but not sent.
- Evidence paths exist for each workstream.
- The actor has a short approval-only dashboard.

## Status

This is a governed AgencyOS Teams project kickoff packet. It is defensible as an operating design artifact, not as proof of a live automated voice-over business system.
