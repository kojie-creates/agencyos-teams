# AgencyOS Teams: Getting Started Guide (V1.0)

## 🌟 Welcome to AgencyOS Teams
AgencyOS Teams is not just an AI chat interface; it is a **Governed Operating Surface**. We provide the framework for your team—whether that's one person or a full department—to collaborate with multiple specialized AI partners, ensuring every output is auditable, compliant, and traceable.

**The Core Value:** Moving AI from "Generating Output" to "Managing Workflows."

### **🚀 I. Before You Begin: Understanding the Surface**
Before running any process, you must understand how AgencyOS operates. Unlike simple LLMs, our system enforces governance at every turn.

*   **AI Being (The Role):** A named, specialized AI persona assigned a specific function (e.g., Researcher, Strategist). Beings have defined inputs, outputs, and boundaries.
*   **Workstream (The Process):** The sequence of tasks that moves the work forward (e.g., "Research $\rightarrow$ Draft $\rightarrow$ Review"). A Workstream is our project pipeline.
*   **Handoff:** The formal act of passing a Workstream artifact from one Being to the next. This handoff *must* be documented, triggering mandatory policy checks.
*   **Artifact & Provenance:** All successful outputs are saved as **Artifacts**, which contain full provenance metadata (who did it, what was done, and why).

### **🛠️ II. Phase 1: Environment Setup (The Installation)**

Follow these steps to set up the local operating surface on your machine.

**Step 1: Prerequisites Check**
Ensure you have Python 3.x and all required dependencies are installed according to `requirements-dev.txt`.

**Step 2: Bootstrap the System**
Run the master bootstrap script from your terminal in the main AgencyOS directory:
```bash
python agencyos_bootstrap.py --host claude "/help"
```
*   This initializes all core services (Policy Engine, Artifact Repository) and verifies connectivity to your chosen LLM host (`--host`).

**Step 3: Define Your Scope**
Before running any serious work, you must define the boundaries of your project using the **Scope Assessment**. This prevents scope creep and ensures the system knows what it is allowed to do.

### **⚙️ III. Phase 2: Running Your First Workstream (The Workflow)**

We recommend starting with a simple Handoff workflow to test the core loop.

1.  **Goal:** Define a single, small task (e.g., "Draft three headlines for an internal memo").
2.  **Initiate Work:** Run the command: `/handoff`
    *   The system will prompt you to define the scope and role owners. **This is mandatory.**
3.  **Observe Gate Checks:** Watch the console output carefully. You must see confirmation that:
    *   Scope/Risk Gates passed successfully.
    *   No external action was taken (Policy success).
4.  **Execute:** The system will route you to the first required Being for execution.

### **🚨 IV. Mandatory Operating Guardrails (DO NOT SKIP)**
These are non-negotiable rules enforced by AgencyOS Teams:

1.  **NEVER TRUST THE OUTPUT BLINDLY:** Assume every piece of text is a draft. Always check the accompanying `[Provenance]` log to see *why* it was generated and what policy governed it.
2.  **EXTERNAL ACTION REQUIRES HUMAN SIGNATURE:** If you intend for the system to send an email, publish content, or call external APIs, the **Policy Gate** will block it by default. You must explicitly trigger a human approval mechanism.
3.  **WORK IS STATEFUL:** Work does not reset when the session closes. All completed work must be formally archived via the `/audit` command to secure its place in the Artifact Repository.

---
***Developed By: The AgencyOS Team Lead Agent***
*For full technical documentation, consult the `./docs/` folder.*