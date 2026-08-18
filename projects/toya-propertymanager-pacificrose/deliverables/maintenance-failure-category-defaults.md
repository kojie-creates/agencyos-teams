# Maintenance Failure Category Defaults

Purpose:

```text
Define the default category priority order for Pacific Rose maintenance visibility, based on older-building conditions, lived-in unit wear, and Kojie's resident experience.
```

Evidence Status:

```text
Source-informed operating hypothesis.
Not a statistical claim until validated against request history.
Volume planning range: 16-20 maintenance requests per month for the larger 60-unit data set.
```

## Larger Data-Set Volume Assumption

```text
Use 16-20 maintenance requests per month as the initial planning range.
Annualized planning range: 192-240 maintenance requests per year.
This range should be replaced by actual Request History counts once available.
```

## Default Priority Categories

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

## Why These Surface First

```text
Plumbing covers hot showers, drainage, leaks, clogs, and likely garbage-disposal escalation.
Appliances covers dishwasher replacement, refrigerator, stove, microwave, trash compactor, and washer/dryer issues.
Water Intrusion/Drywall covers mold, moisture, stains, drywall damage, and hidden deterioration.
Heating & Cooling and HVAC cover winter heat, airflow, comfort, and seasonal risk.
Doors and Windows cover security, drafts, stuck/sliding-door issues, and building-envelope wear.
Electrical covers outlets, lights, breakers, fans, and powered-appliance support.
Pest Control covers recurring unit or common-area pest conditions.
Flooring and Painting capture visible long-term wear in older or non-refurbished units.
```

## Default Routing Tags

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

## Scoring Rule

```text
Default sort order:
1. Safety or habitability risk.
2. Loss of basic living function.
3. Active water, mold, heat, electrical, lock, or pest issue.
4. Repeated issue or unresolved prior request.
5. Affects multiple residents or common areas.
6. Cost likely to increase if delayed.
7. Cosmetic or turnover-condition item.
```

## Validation Needed

```text
Compare defaults against actual Request History exports.
Compare actual monthly count against the 16-20 request planning range.
Track counts by category, sub category, unit, age, recurrence, and completion status.
Adjust default ordering once real request frequency is available.
```
