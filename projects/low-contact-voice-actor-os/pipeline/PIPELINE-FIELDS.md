# Pipeline Fields

## Purpose

Keep outreach, follow-up, evidence, and actor requests out of memory and inside a governed tracker.

## Required Fields

| Field | Rule |
| --- | --- |
| `lead_id` | Stable ID. Do not reuse. |
| `buyer_name` | Company or buyer name. |
| `buyer_category` | Use one controlled category. |
| `city` | Verified locality; nearby LA County cities retain their names. |
| `website` | Public site. |
| `contact_name` | Person if available. |
| `contact_role` | Role or department. |
| `contact_email` | Email only when source is acceptable. |
| `contact_url` | LinkedIn, contact page, staff page, or directory page. |
| `source_url` | Evidence for buyer existence or contact source. |
| `verification_status` | `unverified`, `secondary_source`, `verified`, or `do_not_contact`. |
| `fit_score` | 1-5 after category and use-case review. |
| `outreach_angle` | Specific reason this buyer fits. |
| `status` | Current pipeline state. |
| `last_touch` | Actual successful outbound timestamp only; blank until send evidence exists. |
| `next_touch` | Follow-up due date only after actual initial send; otherwise blank. |
| `required_actor_action` | `none`, `approve_send`, `record_sample`, `price_decision`, `buyer_call`, or `contract_review`. |
| `evidence_link` | Path to source, draft, approval, reply, or closeout artifact. |
| `notes` | Short operational note only. |

## Status Values

- `not_started`
- `drafted`
- `pending_approval`
- `approved_to_send`
- `sent`
- `follow_up_due`
- `replied`
- `sample_requested`
- `recording_needed`
- `quote_needed`
- `call_needed`
- `won`
- `lost`
- `do_not_contact`

## Fit Score

| Score | Meaning |
| --- | --- |
| 5 | Strong recurring need and clear announcer-style fit |
| 4 | Strong service fit; current demand unknown |
| 3 | Possible fit but weaker evidence |
| 2 | Low fit or unclear buyer type |
| 1 | Do not prioritize |

## Actor Contact Rule

Only surface rows where `required_actor_action` is not `none`.

## Evidence Rule

No row moves to `approved_to_send` without:

- Source URL.
- Verified or acceptable secondary-source contact path.
- Outreach draft.
- Claim audit pass.
- Actor approval record.
## Execution Rules

- New columns: draft_updated_at (copy update only), batch_id (exact revision), approval_ref (actor evidence), send_evidence (actual successful send), sample_status (hold or cleared). Empty means unknown; no TBD in dates or scores.
- verified means official service/contact evidence, not a job opening. Scores are operator judgments. Retired shell IDs remain reserved in BUYER-RESEARCH-001.md.
- pending_approval can retain sample holds. approved_to_send additionally requires cleared playback/content evidence and actor approval of exact recipients and revision.
- Copy, recipient, or sample changes invalidate affected approval; retain old revisions and decisions.
- Append contact events with ID, lead ID, batch revision, event type, offset timestamp, recipient, channel, message ID/result, and evidence path. Record initial_sent_at in the initial send event.
- Follow-ups are due three and seven business days after initial_sent_at; skip weekends and US federal holidays using America/Los_Angeles. Never schedule from draft updates. No third follow-up. Follow-up approval is separate.
- Replies pause follow-ups and set replied. Opt-outs suppress contact across batches and set do_not_contact. Bounces are suppressed pending correction. Check duplicate buyer/email and suppression before sending.
- Failed or uncertain sends do not start follow-ups. Resolve uncertain results before retrying.
- decisions/APPROVAL-PACKET-001.md is the single actor decision surface. All paths are relative to project root. These are manual rules; no scheduler is deployed.

