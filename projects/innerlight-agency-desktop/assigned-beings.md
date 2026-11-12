# Assigned Beings

| Being | Handle | Project Role | Workstreams | Approval Limits |
| --- | --- | --- | --- | --- |
| Jaavis | @jaavis | Human-AI interaction point | First routing pass | External API calls, package publishing, installer distribution, destructive git operations, credential handling beyond local safeStorage. |
| Vera | @vera | Governance and evidence reviewer | 05-evidence-closeout | May flag claims and require evidence; cannot approve release alone. |
| Athena | @athena | Orchestration and sequencing | All workstreams | May sequence work; cannot override human gates. |
| Builder Copilot | @builder-copilot | Implementation support | 01-runtime-foundation, 03-ui-operating-loop | May propose and implement scoped diffs; cannot overwrite unrelated work. |
| Architect | @architect | System design and prompt-routing architecture | 02-agent-routing | May define module boundaries; cannot claim implementation evidence without tests. |
| QA Testing | @qa-testing | Verification and regression checks | 04-packaging-release, 05-evidence-closeout | May block closeout on failing or missing evidence. |
| DevOps | @devops | Build and packaging path | 04-packaging-release | May prepare packaging; cannot distribute installers without approval. |
