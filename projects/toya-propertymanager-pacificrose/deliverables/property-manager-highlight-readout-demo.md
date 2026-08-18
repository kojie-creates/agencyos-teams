# Property Manager Highlight Readout - Demo

Audience:

```text
Internal Kojie draft.
Toya/Cirrus-facing only after approval and sanitization.
```

Evidence Status:

```text
Path B demo readout.
Based on sample-request-history-218.csv.
Synthetic sanitized data, not actual Pacific Rose Request History.
```

## Recurring Failures

```text
Top recurring sample categories:
1. Plumbing: 44.
2. Appliances: 40.
3. Water Intrusion/Drywall: 26.
4. HVAC: 22.
5. Heating & Cooling: 20.
```

AgencyOS Teams read:

```text
The sample pattern supports the default assumption that Plumbing and Appliances should be reviewed first.
Water Intrusion/Drywall has lower volume than Plumbing or Appliances but higher risk weight.
```

## Repeat Units

```text
Highest repeat sample units:
Unit sample 20: 4.
Unit sample 21: 4.
Unit sample 22: 4.
Unit sample 23: 4.
Unit sample 24: 4.
Unit sample 25: 4.
Unit sample 26: 4.
Unit sample 27: 4.
Unit sample 28: 4.
Unit sample 29: 4.
```

AgencyOS Teams read:

```text
Repeat-unit watchlists are useful because even a moderate request volume can hide concentrated unit-level deterioration.
Actual Request History should identify whether repeat units are real building signals or sample distribution artifacts.
```

## Aging Infrastructure Signals

```text
Risk-sensitive sample categories:
Plumbing: 44.
Water Intrusion/Drywall: 26.
HVAC: 22.
Heating & Cooling: 20.
Electrical: 17.
```

AgencyOS Teams read:

```text
These categories point to building systems, not just isolated resident complaints.
They should be tagged for capital-wear review when repeated, reopened, or clustered by unit/building.
```

## Seasonal Maintenance Pressure

```text
Monthly sample volume:
Jan: 17.
Feb: 18.
Mar: 18.
Apr: 17.
May: 19.
Jun: 20.
Jul: 18.
Aug: 19.
Sep: 18.
Oct: 17.
Nov: 19.
Dec: 18.
```

AgencyOS Teams read:

```text
The sample stays within the 16-20/month planning band.
Actual Request History should be checked for winter Heating & Cooling pressure, summer HVAC pressure, and rain-linked Water Intrusion/Drywall pressure.
```

## Vendor Dependency

```text
Internal maintenance first: 137.
External vendor likely: 81.
```

AgencyOS Teams read:

```text
Vendor coordination is a major management surface.
AgencyOS Teams should separate onsite triage from vendor-likely work so Toya can see scheduling, cost, and escalation load.
```

## Resident Access Constraints

```text
Permission to enter is present in the maintenance form.
Sample records default to permission-to-enter = Yes.
Access instructions are sensitive resident-provided text.
```

AgencyOS Teams read:

```text
Access instructions should be routed to maintenance but protected from broad reporting.
Failed access attempts should become a follow-up metric once actual history is available.
```

## Pet-Aware Access Needs

```text
Pet present: 72.
Pet not present: 117.
Pet unknown: 29.
```

AgencyOS Teams read:

```text
Pet-aware access is operationally important.
It affects scheduling, entry instructions, technician safety, and resident communication.
It should be visible to work execution but sanitized from management summaries unless needed.
```

## Unresolved Or Reopened Work

```text
Completed: 173.
Open: 29.
Reopened: 16.
Open plus reopened: 45.
```

AgencyOS Teams read:

```text
Open and reopened requests form the first follow-up queue.
Reopened work is the strongest quality signal because it may show failed repair, wrong diagnosis, vendor issues, or recurring infrastructure problems.
```

## Sensitive-Data Boundaries

```text
Sensitive data types already identified:
resident identity
resident payment/balance data
masked payment method
unit/location details
access instructions
pet status
resident-entered descriptions
attachments/photos
```

AgencyOS Teams read:

```text
The Property Manager flavor needs two views:
execution view with operational detail
management view with sanitized summaries
```

## Management Decisions Needed

```text
Approve actual Request History export.
Approve whether unit identifiers should be masked.
Define what Toya can safely share with Cirrus.
Decide whether vendor-likely categories need separate tracking.
Choose thresholds for escalation: age, reopen, repeat unit, water/mold/heat/electrical, or vendor delay.
Choose first pilot: maintenance queue, vendor escalation, resident follow-up, or weekly brief.
```

## Bottom Line

```text
At 218 sample requests/year, AgencyOS Teams should not frame Pacific Rose maintenance as scattered tickets.
It should frame it as building continuity:
what keeps breaking, where it repeats, what needs a vendor, what creates resident friction, and what management needs to decide next.
```
