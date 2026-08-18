# Sample Maintenance Work Orders

Audience:

```text
Internal Kojie draft.
Toya/Cirrus-facing only after approval.
```

Evidence Status:

```text
Sample data only.
Based on previously discussed Pacific Rose maintenance patterns.
Not actual Request History.
```

## Work Order 1

```text
work_order_id: SAMPLE-WO-001
unit_or_location: Unit example, in-unit kitchen
category: Appliances
sub_category: Dishwasher
priority: Medium
submitted_at: sample date
acknowledged_at: sample date
assigned_at: sample date
completed_at: unavailable
status: Open
assigned_to: Maintenance
vendor: TBD
description_summary: Dishwasher is not cleaning properly and may need repair or replacement.
attachment_present: No
permission_to_enter: Yes
pet_present: Yes
reopened: No
resident_rating: unavailable
cost_or_effort: TBD
routing_tags: daily-life-breaker; repeat-failure; resident-access-needed; pet-present; follow-up-required
next_action: Inspect dishwasher, confirm repair vs replacement, document part/vendor need.
```

## Work Order 2

```text
work_order_id: SAMPLE-WO-002
unit_or_location: Unit example, bathroom/shower
category: Plumbing
sub_category: Hot water / shower issue
priority: High
submitted_at: sample date
acknowledged_at: sample date
assigned_at: sample date
completed_at: unavailable
status: Open
assigned_to: Maintenance
vendor: Gas/heating or plumbing vendor if needed
description_summary: Hot shower function is unreliable and affects basic daily use.
attachment_present: No
permission_to_enter: Yes
pet_present: Unknown
reopened: Unknown
resident_rating: unavailable
cost_or_effort: TBD
routing_tags: daily-life-breaker; habitability-risk; vendor-needed; follow-up-required
next_action: Verify hot water condition, determine whether issue is unit-level plumbing or building/system-level service.
```

## Work Order 3

```text
work_order_id: SAMPLE-WO-003
unit_or_location: Unit example, kitchen sink
category: Plumbing
sub_category: Garbage disposal
priority: Medium
submitted_at: sample date
acknowledged_at: sample date
assigned_at: sample date
completed_at: unavailable
status: Open
assigned_to: Maintenance
vendor: TBD
description_summary: Garbage disposal makes grinding noise and appears to require manual adjustment or repair.
attachment_present: Optional
permission_to_enter: Yes
pet_present: Yes
reopened: No
resident_rating: unavailable
cost_or_effort: TBD
routing_tags: daily-life-breaker; repeat-failure; resident-access-needed; pet-present; follow-up-required
next_action: Inspect disposal, verify jam/mechanical issue, repair or escalate for replacement.
```

## Sample Dashboard Readout

```text
Open sample work orders: 3.
Highest priority sample: SAMPLE-WO-002, Plumbing / hot water.
Most common sample category: Plumbing.
Vendor likely needed: SAMPLE-WO-002 if system or gas/heating issue; possible for SAMPLE-WO-001 if replacement is required.
Resident access needed: all sample requests.
Pet-aware access needed: SAMPLE-WO-001 and SAMPLE-WO-003.
```

## Demo Boundary

```text
These samples demonstrate the AgencyOS Teams operating structure.
They should not be represented as actual Pacific Rose work orders.
Replace sample dates, IDs, unit references, and statuses with Request History export values before proof-layer use.
```
