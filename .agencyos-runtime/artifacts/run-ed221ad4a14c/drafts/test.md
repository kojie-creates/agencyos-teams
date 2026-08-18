This workflow is designed to guide you through the manual, step-by-step process of building and deploying a custom LLM agent within an environment like AnythingLLM.

Since the documentation covers the developer journey, the plan is structured into four distinct phases: **Planning**, **Building**, **Testing**, and **Deployment**.

***

## 🚀 Manual Workflow Plan: Building a Custom LLM Agent

### Phase 0: Preparation and Scope Definition (The "What" and "Why")

Before touching any settings or code, you must define the agent's boundaries. This is the most critical manual step to prevent scope creep.

| Step | Goal | Action Items (Manual Work) | Key Output/Checklist Item |
| :--- | :--- | :--- | :--- |
| **0.1 Define Scope** | Determine exactly what the agent will and will not do. | Write a clear, bulleted list of the agent's primary functions (e.g., "It can summarize articles," *but* "It cannot access financial records"). | **Scope Document:** 3-5 clear use cases. |
| **0.2 Identify Tools** | Determine what external capabilities the agent needs to function. | List all necessary external data sources or actions: APIs (e.g., weather, calendar), databases, internal knowledge files. | **Tool Inventory:** API keys gathered; knowledge source locations identified. |
| **0.3 Establish Tone/Persona** | Define how the agent should behave when responding. | Write out a short "persona sheet" (e.g., professional, casual, academic, empathetic). This will inform your System Prompt later. | **Persona Guide:** 1-2 paragraphs describing tone and constraints. |

---

### Phase 1: Agent Core Development (The "Brain")

This phase focuses on configuring the LLM's core instructions—the prompt engineering that tells the agent how to think and respond.

| Step | Goal | Action Items (Manual Implementation) | Verification Check |
| :--- | :--- | :--- | :--- |
| **1.1 Configure System Prompt** | Provide foundational rules for the LLM. | In the Agent Settings, write the comprehensive **System Prompt**. Include: 1) The Persona Guide (0.3), 2) Constraints (What *not* to do), and 3) The Goal Statement (The core mission). | ✅ Does the prompt address role, goals, constraints, and tone? |
| **1.2 Define Logic Flow** | Instruct the agent on its decision-making process. | Add explicit instructions in a section of the System Prompt: "When a user asks X, first you must check Y using Tool Z before generating an answer." This forces structure. | ✅ Is the logic sequential? (e.g., Check $\to$ Process $\to$ Answer). |
| **1.3 Initial Knowledge Base Upload** | Give the agent context to operate on. | Manually upload or point the agent to the initial set of foundational documents relevant to its scope. *Do not over-load it yet.* | ✅ The agent can correctly answer factual questions based *only* on these uploaded files. |

---

### Phase 2: Tool Integration and Logic Linking (The "Hands")

This phase gives your agent the ability to act outside of text generation by connecting it to external systems via custom tools or APIs.

| Step | Goal | Action Items (Manual Implementation) | Verification Check |
| :--- | :--- | :--- | :--- |
| **2.1 Document Tool Schema** | Tell the LLM exactly what capabilities are available and how they work. | For each tool identified in Phase 0 (e.g., a Weather API), write detailed descriptions that include: 1) The function name, 2) What it does, and 3) All required input parameters (and their data types). | ✅ Can you describe the tool's use case without looking at the code? (The description must be clear enough for an LLM to understand.) |
| **2.2 Configure Tool Endpoints** | Connect the descriptions to the live functions. | Manually enter the API endpoints, credentials, and function calling parameters into the developer console/tool setup section of AnythingLLM. | ✅ Does the system correctly validate the keys and connect to the external service? (Test connection outside the chat interface). |
| **2.3 Link Tool Usage** | Force the agent to use the tools when necessary. | Return to the System Prompt (1.1) and add a mandatory instruction: "If the user asks about weather, you *must* use the `get_weather` tool." | ✅ The prompt explicitly mandates tool usage for specific query types. |

---

### Phase 3: Testing, Refinement, and Debugging (The "Polish")

Do not assume it works after setup. Manual testing with varied inputs is crucial to catch logical flaws or ambiguities.

| Step | Goal | Action Items (Manual Execution) | Success Criteria / What to Look For |
| :--- | :--- | :--- | :--- |
| **3.1 Happy Path Testing** | Test the agent's primary, expected use cases. | Input 5-10 simple queries that perfectly fit its defined scope and require tool usage (e.g., "What was the weather in London yesterday?" $\to$ *Uses Weather Tool*). | The agent successfully uses the correct sequence of tools to provide a perfect answer. |
| **3.2 Edge Case Testing** | Test failure scenarios, ambiguity, and out-of-scope requests. | 1) Ask questions it cannot answer (Out of Scope). 2) Give ambiguous queries. 3) Provide bad data inputs. | The agent correctly rejects the query or asks for clarification ("I need more context...") instead of hallucinating an answer. |
| **3.3 Prompt Iteration Loop** | Adjust logic based on test failures. | If the agent fails (e.g., gives a wrong tool, ignores a constraint): *Do not change the code.* Instead, revise the System Prompt to be more restrictive or clearer ("When X happens, you must always do Y"). | The agent's behavior improves in subsequent testing runs without requiring major structural changes. |

---

### Phase 4: Deployment and Monitoring (The "Live" State)

Once testing is complete, finalize the agent for user consumption.

| Step | Goal | Action Items (Manual Finalization) | Outcome/Deployment Checkpoint |
| :--- | :--- | :--- | :--- |
| **4.1 Review Security** | Ensure external data access and API usage are secure. | Verify that all sensitive credentials have been stored securely within the platform's vault, not hardcoded in prompts or exposed in front-end UI elements. | ✅ Credentials are managed via environment variables/vault systems. |
| **4.2 Set User Instructions** | Prepare a simple guide for the end user. | Write clear documentation detailing: 1) What the agent is good at. 2) What the agent cannot do (Setting expectations). | A concise, non-technical "How to use the Agent" guide. |
| **4.3 Final Deployment** | Make the agent available to its intended audience. | Save and publish the customized agent instance. | The final working agent is accessible via the intended channel/interface. |