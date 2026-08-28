# Roles & Responsibilities (Assigned Beings)
**Project:** i9 Sports — AgencyOS Integration

This roster defines the core AI Agents (Beings) and human liaisons responsible for executing this project. Every Being has a defined scope, approval limit, and primary workstream focus to ensure accountability.

| Being | Handle/Handle Type | Primary Role | Workstreams / Expertise | Approval Limits |
| :--- | :--- | :--- | :--- | :--- |
| **operator-team-lead** | `@operator-team-lead` | Central Orchestrator | Project Scoping, Task Routing, Governance Enforcement. | High (System architecture sign-off) |
| **research-coordinator** | `@research-coordinator` | Data Discovery & Benchmarking | Analyzing current state pain points; identifying best practices for scheduling/comms automation. | Medium (Data source validation) |
| **operations-analyst** | `@operations-analyst` | Process Mapping & Feasibility | Translating manual processes into automated workflows; building data flow diagrams. | High (Workflow logic approval) |
| **customer-experience-analyst** | `@cxa-analyst` | User Journey Design | Focus on the end-user experience (Parent/Coach). Ensuring comms are clear and helpful. | Medium (User narrative sign-off) |
| **growth-strategy** | `@grow-strat` | Scalability & Growth Planning | Defining Phase II scope; measuring ROI beyond the pilot's initial goals. | Low (Input only) |
| **learning-coordinator / analytics** | `@learn-ana` | KPI Tracking & Optimization | Collecting, cleaning, and analyzing data from the automated system to measure performance against KPIs. | Medium (Data interpretation sign-off) |
| **truth-agent / risk-and-proof** | `@truth-agent` | Governance & Compliance | Reviewing all outputs for legal adherence, data residency compliance, and functional feasibility checks. | High (Mandatory Gatekeeper approval) |
| **Katie** (Human Point) | N/A | Liaison & Escalation Point | Human validation point for critical decisions; providing qualitative feedback to the team. | Final Authority (Temporary) |

### Initial Operating Sequence:
This sequence represents the mandatory hand-off flow of information and approvals:
1.  `@operator-team-lead`: Defines the initial project parameters and triggers workstreams.
2.  `@research-coordinator`: Gathers raw data on current pain points (Input for Operations).
3.  `@operations-analyst`: Models the 'ideal' workflow and necessary integrations.
4.  `@cxa-analyst`: Vets the modeled workflow from a user experience perspective.
5.  `@truth-agent`: Checks the entire plan against all stated constraints (data residency, legal).
6.  `@growth-strat`: Compiles the approved outputs into the final project brief and roadmap for Brandy's review.