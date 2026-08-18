# Walkthrough: Hospitality Event Venue

Industry:

```text
Independent event venue hosting weddings, corporate events, vendors, catering, staffing, and client walkthroughs.
```

Primary failure modes:

```text
Chaotic intake
Weak handoff
No decision owner
Big deadline
Client promise risk
```

Agencies:

```text
Client Experience AgencyOS
Event Operations AgencyOS
Vendor Coordination AgencyOS
Risk and Proof AgencyOS
```

Configs:

```text
Client Experience: Pod Model by event client.
Event Operations: Assembly Line from inquiry to event closeout.
Vendor Coordination: Hub-and-Spoke for catering, rentals, AV, florals, security, and cleaning.
Risk and Proof: Governance Overlay for contracts, deposits, insurance, capacity, accessibility, and safety.
```

Example request:

```text
@operator We have a 180-person wedding in 30 days. Build the operating plan, vendor handoffs, client communications, and risk checklist.
```

Operator routing:

```text
Scope Gate: one event project with multiple workstreams.
Risk Gate: high, because contract promises, guest safety, vendor dependencies, and deadline risk exist.
Config Selector: Pod Model plus Assembly Line plus Hub-and-Spoke plus Governance Overlay.
Agency Selector: Client Experience owns client communication. Event Operations owns timeline. Vendor Coordination owns vendor handoffs. Risk and Proof checks constraints.
```

Expected outputs:

```text
event run-of-show
vendor handoff packet
client confirmation email
staffing checklist
site readiness checklist
risk and insurance checklist
day-of escalation path
post-event review
```

Continuous improvement:

```text
After event, Insights reviews delays, client feedback, vendor performance, incident notes, and updates venue playbooks.
```

