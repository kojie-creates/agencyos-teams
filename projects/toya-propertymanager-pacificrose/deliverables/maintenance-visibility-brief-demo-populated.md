# Pacific Rose Maintenance Visibility Brief - Demo Populated

Audience:

```text
Internal Kojie draft.
Toya/Cirrus-facing only after approval and sanitization.
```

Evidence Status:

```text
Demo data only.
Uses sanitized synthetic Request History records.
Not actual Pacific Rose Request History.
```

## 1. Weekly / Annual Snapshot

```text
Reporting period: 12-month sample year.
Prepared for: Property Manager flavor, Real Estate -> Property Manager.
Prepared by: AgencyOS Teams demo workflow.
Data source: sample-request-history-218.csv.
Export/capture date: sample data generated locally.
Evidence boundary: synthetic demo proof layer, not operational evidence.
```

## 2. Executive Readout

```text
Projected annual request volume: 218.
Average monthly request volume: 18.17.
Average weekly request volume: 4.19.
Benchmark range: 16-20 requests/month.
Top maintenance theme: Plumbing.
Highest-risk sample categories: Plumbing, Water Intrusion/Drywall, Electrical, Heating & Cooling.
Most repeated failure category in demo: Plumbing.
Vendor-needed sample items: 81.
Internal-maintenance-first sample items: 137.
Resident communication needed: follow-up queue for open and reopened work.
Decision needed from Toya/Cirrus: approve actual Request History export for validation.
```

## 3. Monthly Volume Projection

| Month | Requests |
| --- | ---: |
| Jan | 17 |
| Feb | 18 |
| Mar | 18 |
| Apr | 17 |
| May | 19 |
| Jun | 20 |
| Jul | 18 |
| Aug | 19 |
| Sep | 18 |
| Oct | 17 |
| Nov | 19 |
| Dec | 18 |
| Total | 218 |

Interpretation:

```text
The demo stays inside the 16-20 requests/month planning band.
At this volume, maintenance is a continuous operating stream, not an occasional task.
```

## 4. Default Failure Category View

| Category | Sample Total | Completed | Open | Reopened | Operating Read |
| --- | ---: | ---: | ---: | ---: | --- |
| Plumbing | 44 | 35 | 6 | 3 | Highest recurring daily-life and habitability signal. |
| Appliances | 40 | 31 | 6 | 3 | Strong resident-impact signal, especially dishwasher and disposal-type issues. |
| Water Intrusion/Drywall | 26 | 22 | 2 | 2 | Risk-sensitive deterioration and mold/moisture watch area. |
| HVAC | 22 | 17 | 3 | 2 | Seasonal comfort and vendor-dependency signal. |
| Heating & Cooling | 20 | 16 | 3 | 1 | Heat-readiness and comfort risk. |
| Doors and Windows | 18 | 13 | 3 | 2 | Security, drafts, sliding door, and envelope-wear signal. |
| Electrical | 17 | 15 | 1 | 1 | Safety-sensitive infrastructure signal. |
| Pest Control | 13 | 10 | 2 | 1 | Recurrence and common-area watch area. |
| Flooring | 10 | 7 | 2 | 1 | Long-term wear and turnover-condition signal. |
| Painting | 8 | 7 | 1 | 0 | Lower urgency, useful for condition planning. |

## 5. Request Queue Sample

| Work Order | Unit / Location | Category | Sub Category | Priority | Status | Owner | Risk Tag | Next Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SAMPLE-RH-0001 | Unit sample 01 | Plumbing | Garbage disposal | High | Completed | Maintenance | habitability-risk | Use as completed reference pattern. |
| SAMPLE-RH-0045 | Unit sample 45 | Appliances | Refrigerator | Medium | Open | Maintenance | daily-life-breaker | Confirm repair vs replacement path. |
| SAMPLE-RH-0088 | Unit sample 28 | Water Intrusion/Drywall | Wall moisture | High | Reopened | Maintenance + vendor | habitability-risk | Escalate for moisture/mold review. |

## 6. Routing Tag Summary

| Routing Tag | Count | Meaning |
| --- | ---: | --- |
| habitability-risk | 107 | Water, heat, plumbing, electrical, or similar risk-sensitive work. |
| follow-up-required | 71 | Lower-risk work still needing queue management. |
| daily-life-breaker | 40 | Appliance failures that directly affect resident use. |

## 7. Vendor Load

| Owner Type | Count | Use |
| --- | ---: | --- |
| Internal maintenance first | 137 | Onsite or maintenance-person triage. |
| External vendor likely | 81 | Vendor coordination, schedule, and cost visibility. |

## 8. Property Manager Continuity Signals

```text
Plumbing and Appliances dominate the sample set.
Water Intrusion/Drywall is lower volume but higher risk.
HVAC and Heating & Cooling should be watched seasonally.
Doors and Windows, Flooring, and Painting show building-envelope and wear patterns.
Open and reopened items become the first follow-up queue.
Vendor-likely items become the first escalation queue.
```

## 9. Proof-Layer Questions

```text
Does actual Request History also show Plumbing and Appliances as the top categories?
Do Water Intrusion/Drywall records cluster in specific units or buildings?
Do HVAC and Heating & Cooling spike seasonally?
Which units repeat across categories?
Which vendors appear most often?
Which request types reopen most often?
Which categories age longest before completion?
```

## 10. Toya/Cirrus Decision Queue

```text
Approve safe Request History export.
Confirm whether unit identifiers should be masked in demo views.
Confirm whether resident descriptions can be summarized by AgencyOS Teams.
Confirm vendor/cost fields available in Cirrus or RENTCafe systems.
Choose first pilot: maintenance queue, vendor escalation, resident follow-up, or weekly brief.
```

## Demo Boundary

```text
This populated brief demonstrates what AgencyOS Teams can produce.
It does not prove Pacific Rose's actual historical maintenance distribution.
Replace sample-request-history-218.csv with actual Request History before making performance, compliance, vendor, or capital-planning claims.
```
