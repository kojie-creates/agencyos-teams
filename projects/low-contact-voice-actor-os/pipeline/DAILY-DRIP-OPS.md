# Daily VO Lead Drip

Operating parameters for weekday automation (DAILY-DRIP-v1).

| Param | Value |
| --- | --- |
| Daily target | 10 initial emails |
| Days | Mon–Fri, America/Los_Angeles |
| Mailbox | felix.montanez@hotmail.com |
| Approval | Standing (decisions/STANDING-APPROVAL-DAILY-DRIP-v1.md) |
| Lead source | market-intel/sources secondary CANDIDATE rows; primary LEAD-TRACKER owns sends |
| Sample | cleared CloudFront VO sample (E-014) |
| Follow-up calendar | FU1 +3 business days; FU2 +7 business days; 9–10am PT blocks |
| Routine | vo-daily-lead-drip |

Artifacts per run: outreach/OUTREACH-BATCH-NNN.md, decisions/APPROVAL-PACKET-NNN.md (stamped standing), evidence/OUTLOOK-SEND-NNN.json, calendar evidence as needed.
