# Pacific Rose Maintenance Visibility Brief Template

Audience:

```text
Internal Kojie draft first.
Toya/Cirrus-facing only after approval and sanitization.
```

Purpose:

```text
Show how AgencyOS Teams can turn RENTCafe maintenance requests and request history into a weekly operating view for Pacific Rose.
```

Evidence Status:

```text
Template only.
Uses confirmed portal/form structure plus source-informed defaults.
No performance claim until populated with actual Request History export.
Planning volume uses 16-20 maintenance requests per month as an operating assumption for the larger data set.
```

## 1. Weekly Snapshot

```text
Reporting period:
Prepared for:
Prepared by:
Data source:
Export/capture date:
Evidence boundary:
```

## 2. Executive Readout

```text
Top maintenance theme:
Highest-risk open issue:
Oldest unresolved issue:
Most repeated failure category:
Units with repeat issues:
Common-area issues:
Vendor-needed items:
Monthly request volume:
Benchmark range: 16-20 requests/month.
Resident communication needed:
Decision needed from Toya/Cirrus:
```

## 2A. Larger Data-Set Planning Assumption

```text
Use 16-20 maintenance requests per month as the initial larger-data-set planning range for a 60-unit Pacific Rose operating model.
Annualized range: 192-240 maintenance requests per year.
Use this only as a planning assumption until actual Request History validates volume.
```

Interpretation:

```text
Below 16/month: lower-than-benchmark volume or under-reporting may be present.
16-20/month: expected planning band for Pacific Rose until proven otherwise.
Above 20/month: high-wear, deferred-maintenance, seasonal, or communication/access friction may be present.
```

## 3. Default Failure Category View

Use this order before Request History validates actual frequency:

```text
1. Plumbing.
2. Appliances.
3. Water Intrusion/Drywall.
4. Heating & Cooling.
5. HVAC.
6. Doors and Windows.
7. Electrical.
8. Pest Control.
9. Flooring.
10. Painting.
```

Default interpretation:

```text
Plumbing: hot showers, drainage, leaks, clogs, garbage disposal.
Appliances: dishwasher, refrigerator, stove, microwave, trash compactor, washer/dryer.
Water Intrusion/Drywall: mold, moisture, stains, drywall damage.
Heating & Cooling / HVAC: heat, airflow, comfort, seasonal readiness.
Doors and Windows: locks, sliding doors, seals, drafts, security.
Electrical: outlets, breakers, lights, fans, powered-appliance support.
Pest Control: recurring unit or common-area pest conditions.
Flooring / Painting: long-term wear, turnover condition, non-refurbished unit condition.
```

## 4. Request History Proof Fields

Minimum useful fields:

```text
work_order_id
unit_or_location
category
sub_category
priority
submitted_at
acknowledged_at
assigned_at
completed_at
status
assigned_to
vendor
description_summary
attachment_present
permission_to_enter
pet_present
reopened
resident_rating
cost_or_effort
```

If unavailable:

```text
Mark field as unavailable.
Do not infer missing values.
Use screenshot/export evidence label.
```

## 5. Maintenance Queue

| Work Order | Unit / Location | Category | Sub Category | Priority | Status | Age | Owner | Risk Tag | Next Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD |

Sample rows:

| Work Order | Unit / Location | Category | Sub Category | Priority | Status | Age | Owner | Risk Tag | Next Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SAMPLE-WO-001 | Unit example, kitchen | Appliances | Dishwasher | Medium | Open | TBD | Maintenance | daily-life-breaker; repeat-failure | Inspect dishwasher, confirm repair vs replacement. |
| SAMPLE-WO-002 | Unit example, bathroom/shower | Plumbing | Hot water / shower issue | High | Open | TBD | Maintenance / vendor | daily-life-breaker; habitability-risk | Verify hot water issue and determine unit vs system cause. |
| SAMPLE-WO-003 | Unit example, kitchen sink | Plumbing | Garbage disposal | Medium | Open | TBD | Maintenance | daily-life-breaker; resident-access-needed | Inspect disposal, repair jam or escalate replacement. |

## 6. Category Counts

| Category | Open | Completed | Reopened | Repeat Units | Avg Age | Notes |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| Plumbing | TBD | TBD | TBD | TBD | TBD | TBD |
| Appliances | TBD | TBD | TBD | TBD | TBD | TBD |
| Water Intrusion/Drywall | TBD | TBD | TBD | TBD | TBD | TBD |
| Heating & Cooling | TBD | TBD | TBD | TBD | TBD | TBD |
| HVAC | TBD | TBD | TBD | TBD | TBD | TBD |
| Doors and Windows | TBD | TBD | TBD | TBD | TBD | TBD |
| Electrical | TBD | TBD | TBD | TBD | TBD | TBD |
| Pest Control | TBD | TBD | TBD | TBD | TBD | TBD |
| Flooring | TBD | TBD | TBD | TBD | TBD | TBD |
| Painting | TBD | TBD | TBD | TBD | TBD | TBD |

## 7. Routing Tags

```text
daily-life-breaker
habitability-risk
repeat-failure
vendor-needed
resident-access-needed
pet-present
photo-or-attachment-needed
capital-wear-signal
follow-up-required
```

## 8. Risk And Escalation View

| Issue | Why It Matters | Evidence | Recommended Escalation | Approval Needed |
| --- | --- | --- | --- | --- |
| TBD | TBD | TBD | TBD | TBD |

Escalate for review when:

```text
Water, mold, heat, lock/security, electrical safety, pest recurrence, unresolved repeat issue, or resident financial/privacy data appears.
```

## 9. Resident Communication Draft Queue

| Request | Audience | Draft Type | Sensitive Data Present | Approval Needed |
| --- | --- | --- | --- | --- |
| TBD | Resident | Status follow-up | TBD | Yes |
| TBD | Vendor | Work clarification | TBD | Yes |
| TBD | Toya/Cirrus | Management summary | TBD | Yes |

Rules:

```text
No message is sent automatically.
Use sanitized summaries unless Kojie approves exact resident evidence.
Do not include payment details, personal resident data, access instructions, or pet status externally without approval.
```

## 10. Proof-Layer Validation

Questions to answer after Request History is available:

```text
Does actual monthly volume fall inside the 16-20 request planning range?
Do actual requests cluster around the default failure categories?
Which categories are most frequent?
Which categories age longest before completion?
Which categories reopen most often?
Which units show repeat failures?
Which failures require vendors?
Which issues appear seasonal?
Which issues signal capital work instead of one-off maintenance?
```

## 11. Decisions Needed

```text
Can Request History be exported safely?
Can category/sub-category mappings be captured across all categories?
Can Toya/Cirrus receive a sanitized pilot brief?
Can resident-identifying data be removed before external use?
Which workflow should be piloted first: maintenance queue, weekly brief, vendor escalation, or resident follow-up?
```

## 12. AgencyOS Teams Output

```text
Weekly maintenance visibility brief.
Open issue queue.
Failure category trend view.
Repeat-unit watchlist.
Vendor escalation list.
Risk/evidence exceptions.
Toya/Cirrus decision queue.
Sanitized resident communication drafts.
```
