# FluidLogic Elite Athlete Transition — AgencyOS Teams + Grok Walkthrough

**Operator:** Jaavis (`@operator`)  
**Date:** 2026-09-03  
**Client / company:** Juan Benitez / FluidLogic  
**Human gates:** Juan (commercial owner) and Kojie (AgencyOS owner)  
**Project packet:** `projects/fluidlogic-agencyos-integration/`  
**Prior workthrough:** `agencyos-pro/workthroughs/fluidlogic-elite-athlete-market-transition.md`

This file is the **operating guide Juan can run with a small team**. It does not replace the existing packet. It maps AgencyOS agencies onto named Beings and the Grok bots that already exist, and it tells you what to paste, what to file, and when to stop.

---

## 1. What this is (and is not)

FluidLogic is not a beverage or wellness brand. Public site (`https://fluidlogic.com/`) frames **Intelligent Hydration™** as systems that dose water when the body needs it, integrated with athlete or vehicle.

Verified public facts (do not inflate):

| Fact | Source |
| --- | --- |
| VMR is an in-vehicle, hands-free hydration system used in NASCAR, IndyCar, IMSA, WEC, off-road | fluidlogic.com VMR product + 2026 season post |
| GPR50 is a wearable pack: in-helmet delivery, handlebar remote, haptic prompts, app-estimated sweat plan | fluidlogic.com GPR50 |
| Named off-road proof: Mark Samuels, Ciaran Naran, Ryan Arciero (Baja / SCORE) | fluidlogic.com homepage |
| 2026 editorial: NASCAR / IndyCar / IMSA / off-road presence | fluidlogic.com/blogs/news/a-winning-start-to-2026-... |
| CEO Sara Blackmer (public) has described GPR50 as the same foundational tech as professional motorsports, aimed at a broader performance audience | BikeMag GPR50 review |

**Not verified from this pass:** Juan's exact title/role (LinkedIn was not treated as scraped evidence). Treat his role as **commercial / client owner** until he confirms.

**Definition of done for this request:** Juan has a walkthrough he can follow — agents, order, outputs, prompts, handoffs, wellness-avoidance, race-proof preservation, research-to-GTM, and a post-launch learning loop.  
**Definition of done for the market transition itself:** not assets published. Direct market signal, a narrow pilot, proof-safe claims, and a continue / revise / stop decision.

---

## 2. How to run this with Grok bots

AgencyOS Teams is the **folder and rules**. Grok bots are the **named people**.

Talk to **Jarvis / Jaavis** first (`@operator`). That is intake and closeout. Do not start in Content.

| AgencyOS job | Being | Grok bot today | Notes |
| --- | --- | --- | --- |
| Intake / closeout | Jaavis `@operator` | **Jarvis** | Always start and end here |
| Orchestration | Athena `@athena` | **Athena** | Sequence, gates, no specialist depth |
| Evidence / claims | Vera `@vera` | **Vera** | Claim grades; not existence-close |
| Closeout stamp | Soren Gate `@soren-gate` | **Soren Gate** | Binary: artifact exists or not |
| Research coord | Atlas `@atlas` | *not created* — invoke as skill / prompt | Coordinator only |
| Market intel | Selene Cross `@selene-cross` | *skill / prompt* | Specialist under Atlas |
| Research analyst | Corin Vale `@corin-vale` | *skill / prompt* | Specialist under Atlas |
| Strategy | Adrian Ledger `@adrian-ledger` + Athena | Athena + prompt | Beachhead + narrative |
| Growth / GTM coord | Miles `@miles` | *not created* | Coordinator |
| Marketing strategy | Lyra North `@lyra-north` | *skill / prompt* | |
| Content | Aria Bloom `@aria-bloom` | *skill / prompt* | After claim matrix |
| Sales enablement | Theo Close `@theo-close` | *skill / prompt* | |
| Experiment / pilot | Pax Trial `@pax-trial` | *skill / prompt* | |
| Customer insight | Nina Door `@nina-door` | *skill / prompt* | |
| Learning loop | Elias `@elias` | *not created* | Coordinator |
| Risk | Ronan Shield `@ronan-shield` | Vera + Soren | Overlay, not a phase you skip |

Engineering bots (Bob, Cassian, Mason, Iris) stay **off this lane** unless a product/app change is in scope.

**Small-team rule:** Juan + one operator (Kojie / Jarvis) is enough. Do not spawn every specialist as a sidebar bot. Paste the phase prompt into Jarvis or Athena and name the Being. Create Atlas / Miles / Elias as Grok teammates only if this lane stays weekly.

**Paste this into Jarvis to start any phase:**

```text
@operator Route this through AgencyOS Teams project fluidlogic-agencyos-integration.
Use [Being handle]. File outputs in the matching workstream folder.
Do not jump to content. Do not use wellness language.
Preserve race-proven VMR / GPR50 proof. Juan is commercial owner.
```

---

## 3. Order of work (do not skip)

```text
0  Jaavis          intake + scope (this brief)
1  Athena          routing map + gates
2  Atlas lane      research (Selene + Corin)
   Vera            claim matrix in PARALLEL with research
3  Athena + Adrian positioning (after research v1)
4  Pax             narrow elite-athlete pilot
5  Theo            sales enablement for THAT pilot
6  Aria            only the assets the pilot needs
   Vera            review every public sentence
7  Miles           targeted launch (no broad paid)
8  Elias + Nina    learning from first reply, not after "launch"
9  Soren           close only if files exist
   Juan / Kojie    human gate: continue / revise / stop
```

Content before research is a failure. Launch before a claim matrix is a failure.

---

## 4. Phase cards — prompt, produce, hand off

Copy the **Handoff packet** at the bottom of each phase into `projects/fluidlogic-agencyos-integration/handoffs/`.

### Phase 0 — Jaavis / Jarvis (`@operator`)

**Job:** Lock scope. Name the packet. Name the human. Block wellness and overclaim.

**Prompt (already satisfied by this brief; reuse if the work restarts):**

```text
You are Jaavis, AgencyOS operator.

Client: Juan Benitez, FluidLogic (https://fluidlogic.com/).
Task: walkthrough for moving from motorsports credibility into elite athletes.
Constraint: small team, no generic wellness, keep race-proven proof.
Do not execute a full GTM. Produce the operating walkthrough and file it in the FluidLogic packet.
```

**Produces:** this guide; project link; risk note (performance / athlete-health claims).

**Hands to:** Athena.

**Pause if:** Juan is not named as commercial owner, or someone asks to "just write ads."

---

### Phase 1 — Athena (`@athena`)

**Job:** Turn the brief into a routed plan. Prevent content-first work.

**Prompt:**

```text
You are Athena, Central Orchestrator for FluidLogic's elite athlete transition.

Verified public base:
- Intelligent Hydration™ systems, integrated with athlete or vehicle
- VMR: vehicle-mounted, NASCAR / IndyCar / IMSA / WEC / off-road
- GPR50: wearable, handlebar remote, haptic prompts, app plan; SCORE / hard enduro / GNCC
- Do not treat 2026 race wins as FluidLogic-caused. Presence is verified; causation is not.

Create a routed work plan using:
Atlas (research), Vera (risk/proof), Adrian/Athena (positioning),
Pax (pilot), Theo (sales), Aria (content), Miles (launch), Elias (insights), Soren (close).

For each: job, inputs, outputs, handoff recipient, approval gate, evidence requirement.
Keep motorsports proof central. Separate verified facts, assumptions, and claims needing validation.
Do not recommend a wellness beachhead.
```

**Produces:** agency routing map, sequence, owners, evidence requirements, approval gates.

**Hands to:** Atlas + Vera in parallel.

**File in:** `workstreams/research/` and packet `plan/`.

---

### Phase 2 — Atlas (`@atlas`) with Selene + Corin

**Job:** Find where elite-athlete demand may exist. Not "who drinks more water."

**Research lanes (fan out, then Atlas merges):**

- Heat + hydration pressure in a sport
- Training/competition interruption (hands, helmet, rules)
- Equipment compatibility (GPR50 vs VMR vs neither)
- Coach / performance-staff influence
- Recovery vs safety language (do not medicalize)
- Team budget / procurement
- Current hydration behavior
- What actually transfers from race-car / Baja proof

**Prompt:**

```text
You are Atlas (Research Coordinator) for FluidLogic.

Research elite athletes for race-proven intelligent hydration — timely, low-friction, performance-integrated, coach-visible, compatible with intense training or competition.

Do not research generic wellness buyers or "everyday hydration."

Segment by: sport or athlete type, hydration pain, decision-maker, influencer, buying trigger, proof needed, objection, best first pilot.

Prioritize segments where hands-free or timed dosing is an operational problem (heat + focus + gear), not a lifestyle preference.

Create one opportunity map. Flag anything that requires a real athlete, coach, or team conversation. Do not invent win-rate or market-size numbers.
```

**Produces:** opportunity map, buyer/influencer map, language bank, objections, pilot shortlist, research gaps.

**Hands to:** Athena (positioning), Pax (pilot), Vera (claims).

**File in:** `workstreams/research/` and `deliverables/fluidlogic-research-market-analysis/` (update, don't ghost the Aug 18 draft).

---

### Phase 2b — Vera (`@vera`) overlay (start with research, stay forever)

**Job:** Grade claims. Protect race-proven credibility from becoming "we make you faster."

**Prompt:**

```text
You are Vera, evidence lead for FluidLogic.

Classify every draft claim as:
verified public fact | internally supportable | customer anecdote | hypothesis | too strong / prohibited.

Build a claim language guide: approved terms, terms to avoid, evidence needed, safer alternatives.

Protect: race-proven systems, intelligent / strategic hydration, low-distraction access, heat / focus / timing, performance environment.

Reject: wellness, hydration journey, feel your best, balance, self-care, biohack, guaranteed gains, implied medical outcomes.

Do not treat 2026 NASCAR/IndyCar wins as product causation unless FluidLogic can show a sourced, approved attribution.
Named Baja quotes (Samuels, Naran, Arciero) are anecdotes — usable as testimony, not as universal performance proof.
```

**Produces:** claim matrix, approved/blocked language, evidence gaps, review notes on every public asset.

**Hands to:** everyone who writes a sentence Juan might send.

---

### Phase 3 — Positioning (Athena + Adrian Ledger)

**Job:** Translate motorsports into elite-athlete relevance. Do not bury the race story. Do not become a supplement brand.

**Frame (from existing packet — keep unless research kills it):**

```text
From hydration-as-habit  →  hydration-as-performance infrastructure
From race conditions     →  high-intensity athletic environments
From convenience         →  precision access at the moment performance demands it
```

**Prompt:**

```text
You are the Strategy / Positioning lane (Athena + Adrian Ledger).

Inputs: Atlas opportunity map, Vera claim matrix, existing positioning draft in
projects/fluidlogic-agencyos-integration/deliverables/fluidlogic-positioning-draft/.

Create a premium elite-athlete positioning system:
beachhead segments, positioning statement, core narrative, messaging pillars,
proof pillars, category language, before/after, words to use, words to avoid,
how VMR and GPR50 proof transfers (and where it does not).

Tone: sleek, polished, premium, performance-first. Apple clarity, Nike Run discipline.
Do not use generic wellness. Do not bury motorsports. Translate it.
If research says the first beachhead is still two-wheel / heat-endurance rather than
track-and-field, say so. Do not force a fashion-athlete persona.
```

**Produces:** positioning system, brand language, segment priority.

**Hands to:** Pax, Theo, Aria. **Human pause:** Juan approves beachhead before assets.

**File in:** `workstreams/positioning/`.

---

### Phase 4 — Pax Trial (`@pax-trial`) — offer + pilot

**Job:** One narrow test. 10–20 users. Learning over scale.

**Prompt:**

```text
You are Pax Trial, Offer and Pilot Design for FluidLogic.

Inputs: opportunity map, positioning, claim matrix.

Design ONE first elite-athlete pilot:
thesis, ideal participant, inclusion/exclusion, onboarding, usage instructions,
feedback questions, success signals, failure signals, team roles, timeline,
post-pilot continue/revise/stop rules.

Keep it narrow. Do not promise performance improvement.
Prefer a use case where hands-free or timed dosing is already an operational pain
(heat + helmet/hands + duration), so GPR50 or a defined derivative can be tested honestly.
White-glove onboarding. Weekly check-in. Post-pilot proof review.
```

**Produces:** pilot brief, profile, feedback form, success/failure criteria, calendar, decision rules.

**Hands to:** Theo, Miles, Elias, Vera.

**File in:** `workstreams/pilot-design/` (update existing brief).

---

### Phase 5 — Theo Close (`@theo-close`) — sales enablement

**Job:** Equip Juan to talk to athletes, coaches, trainers, performance directors — not Instagram.

**Prompt:**

```text
You are Theo Close, Sales Enablement for FluidLogic.

Create assets for the elite-athlete PILOT only (not a national launch).

Inputs: positioning, pilot brief, claim matrix, opportunity map.

Create: outreach scripts by buyer type, conversation guide, discovery questions,
objection responses, one-page pilot overview, follow-up emails, referral ask,
call-notes template.

Premium and specific. Preserve race-proven systems.
Ban: optimize your lifestyle, stay balanced, feel your best, hydration journey.
```

**Produces:** scripts, discovery guide, objections, one-pager, follow-ups, call notes.

**Hands to:** Miles, Elias, Vera.

---

### Phase 6 — Aria Bloom (`@aria-bloom`) — content studio

**Job:** Only assets the pilot needs. Every claim maps to Vera's matrix.

**Minimum set:**

- Elite-athlete landing outline (not a full site rebuild)
- Race-proven proof section (VMR + named off-road quotes, labeled as testimony)
- Pilot invitation
- Short LinkedIn sequence
- Founder / operator narrative
- Coach / performance-staff explainer
- Case-study template (empty until a pilot produces evidence)
- FAQ

**Prompt:**

```text
You are Aria Bloom, Content Studio for FluidLogic.

Inputs: positioning, claim matrix, pilot design, sales notes.

Create the minimum asset list above.
Constraints:
- no generic wellness
- no unsupported performance claims
- motorsports proof appears early
- copy is precise, disciplined, premium
- annotate every claim with its Vera grade
```

**Produces:** outlines, copy blocks, social sequence, FAQ, case-study template, claim annotations.

**Hands to:** Miles, Vera (mandatory before anything public), Elias.

**Human pause:** Juan approves public copy.

---

### Phase 7 — Miles (`@miles`) — launch

**Job:** Targeted activation. Capture every response. No broad paid until the message survives live conversations.

**Prompt:**

```text
You are Miles, Growth / Launch coordinator for FluidLogic.

Plan the first elite-athlete pilot launch.

Inputs: approved beachhead, pilot brief, outreach scripts, content, claim matrix.

Create: launch list structure, daily outreach plan, channel plan, referral plan,
follow-up cadence, response-tracker fields, escalation rules, weekly review agenda.

Narrow enough for Juan plus one operator. Do not recommend broad paid campaigns yet.
```

**Produces:** launch plan, tracker, cadence, weekly agenda.

**Hands to:** Elias, Athena, Vera.

**File in:** `workstreams/launch-ops/`.

---

### Phase 8 — Elias (`@elias`) + Nina (`@nina-door`) — learning loop

**Job:** Turn replies into decisions. Start at first outreach, not after a "launch party."

**Track:** who responded / ignored / referred; fastest-understood segment; words that worked or confused; repeating objections; urgent use cases; over-broad pilot criteria; claims that needed more proof.

**Prompt:**

```text
You are Elias (Insights) with Nina Door (Customer Insight) for FluidLogic.

Review outreach, calls, pilot feedback, objections, usage notes.

Weekly learning report:
strongest / weakest segment, best / confusing language, repeated objections,
proof gaps, usage themes, recommended changes to positioning / offer / assets,
continue | revise | stop.

Send recommended changes to Athena before anyone updates public assets.
```

**Produces:** weekly report, message-test notes, segment signals, revision notes, decision recommendation.

**Hands to:** Athena, then the agency that must change. Vera before public edits.

**File in:** `workstreams/learning-loop/`.

---

### Phase 9 — Soren Gate (`@soren-gate`) then humans

**Job:** Existence check. Generated text is not completion.

**Prompt:**

```text
You are Soren Gate.

For this FluidLogic walkthrough closeout, verify these artifacts exist on disk
and are reachable (path + yes/no). Inference is not proof.

Required:
- this walkthrough
- project packet folders
- agencyos-pro workthrough
- handoff record for this run
```

**Then Juan / Kojie:** accept, reject, or change scope.  
**Market transition** still needs the later artifacts (opportunity map update, live claim matrix, approved beachhead, pilot in-market).

---

## 5. Handoff packet (use every time)

```text
Handoff ID:
Date:
Workstream: research | positioning | pilot-design | launch-ops | learning-loop
Source Being:
Destination Being:
Reason:
Input provided (paths):
Expected output:
Dependencies:
Risk level:
Approval needed: Juan | Kojie | none
Evidence status: verified | anecdote | hypothesis | missing
Closeout status: draft | ready | in_progress | blocked | returned | closed
```

Rules: preserve context, name the next owner, name evidence, flag approval, never imply completion.

---

## 6. How to avoid generic wellness

If a sentence would fit a vitamin brand, delete it.

**Use:** race-proven systems, intelligent / strategic hydration, low-distraction access, performance environment, heat / load / focus / timing, competition-ready, training-integrated, validated in demanding environments.

**Avoid:** wellness, hydration journey, feel your best, healthy lifestyle, self-care, balance, generic recovery, biohack, miracle performance, guaranteed gains.

**Translate, don't bury, motorsports:**

```text
Motorsports is the harshest proof environment FluidLogic already has —
heat, focus, gear, and split-second decisions in one cockpit.
That is a transfer thesis for other elite contexts. It is not automatic proof
that a marathoner's kit should look like a Cup car.
Test the transfer in a narrow pilot. Do not advertise it as done.
```

**Do not** claim 2026 wins as FluidLogic outcomes. Presence in those series is public. Causation is not.

---

## 7. Research-to-GTM (one page)

1. Atlas finds high-pressure athlete segments.  
2. Athena / Adrian turn findings into premium positioning.  
3. Vera checks claims **before** assets.  
4. Pax designs a 10–20 person test.  
5. Theo prepares conversations.  
6. Aria makes only test assets.  
7. Miles runs targeted outreach.  
8. Elias reads response and usage.  
9. Athena routes revisions.  
10. Vera approves updated public claims.  
11. Juan decides continue / revise / stop.

Automation that is safe without Juan: research merge, attaching the claim matrix to later phases, filing handoffs, drafting scripts.  
**Must pause for a human:** beachhead choice, public copy, pilot budget/scope, performance or safety claims, spend, continue/revise/stop.

---

## 8. Weekly cadence (Juan + one operator)

| Day | Who | What |
| --- | --- | --- |
| Mon | Athena / Jarvis | Priorities for the week |
| Tue | Atlas or Miles | Research or list update |
| Wed | Theo | Calls and objections |
| Thu | Aria | Assets **only if** learning says so |
| Fri | Elias | Learning report |
| Before any public change | Vera | Claim review |

**Decision rules:**

- **Continue** if a segment understands fast and asks about pilot details.  
- **Revise** if interest exists but use case or language is muddy.  
- **Stop** if hydration is low urgency or the system can't be adopted operationally.  
- **Escalate** if any performance, medical, safety, or athlete-health claim outruns evidence.

---

## 9. What already exists in the packet (do not ignore)

Aug 18 packet under `projects/fluidlogic-agencyos-integration/`:

- intake, plan, assigned agencies/beings  
- deliverables: research-market-analysis, positioning-draft, risk-proof-claim-review, market-entry-wedge-options, pilot-concept, pilot-brief, launch-playbook  
- workstreams: research, positioning, pilot-design, launch-ops, learning-loop  
- evidence ledger, handoffs, closeout stubs  

Those drafts are **starting files**, not live market proof. Update them in place when a phase completes.

---

## 10. Evidence status for this operator run

| Claim | Status |
| --- | --- |
| Walkthrough requested by brief | verified (this chat) |
| FluidLogic public product + series presence | verified (fluidlogic.com, 2026-09-03 fetch/search) |
| Named Baja quotes on homepage | verified as published testimony |
| Elite-athlete beachhead identity | **hypothesis** — needs Atlas + Juan |
| Grok roster covering Athena, Vera, Soren, Jarvis | verified (created 2026-09-03) |
| Atlas / Miles / Elias / content-sales specialists as Grok bots | **not created** — run as prompts |
| Full GTM executed | **not done** — out of scope for this close |

---

## 11. Next action for Juan

1. Approve this walkthrough (Kojie human gate on the operating method).  
2. Confirm beachhead **after** one Atlas research pass — do not pick "all elite athletes."  
3. Optional: stand up Atlas, Miles, and Elias as Grok teammates if this becomes weekly.  
4. Do not publish landing copy until Vera stamps the claim matrix.

Operator close: walkthrough filed. Market transition remains open.

---

## Human gate

- Decision: **ACCEPT** (operating method)
- Owner: Kojie
- Time: 2026-09-03 4:15 PM PT
- Market transition remains open. Beachhead still requires Juan after research.
