# 🚀 LM Studio Local Setup Validation Runbook

**(Internal Use Only)**

This runbook guides users through validating a newly installed local LLM environment using LM Studio before integrating it into team workflows or relying on its output for critical tasks. The goal is to ensure stability, performance, and expected functionality across various models.

---

### 🎯 Scope & Goal

**Goal:** To confirm that the selected hardware, operating system, model weights, and LM Studio installation are functioning together correctly under realistic load conditions.
**Target Environment:** [Specify OS: e.g., Windows/Mac/Linux]
**Required Hardware Check:** Stable GPU VRAM availability (Ideally ≥ 12GB for larger models).

### ✅ Phase 0: Pre-flight Checklist (Setup Verification)

*   [ ] **System Requirements:** Confirm that the GPU drivers are fully updated and recognized by LM Studio.
*   [ ] **LM Studio Version:** Verify the current version matches the latest stable release ([Specify version if necessary]).
*   [ ] **Model Weights Integrity:** Downloaded model file (`gguf` format) is complete and verifiable (no checksum errors).
    *   *Note:* Use a standard, reliable base model for initial testing (e.g., Mistral 7B or Llama 3 8B).

### ⚙️ Phase 1: Technical Stability & Performance Test

**Objective:** Measure basic operational stability and throughput before running complex prompts.

| Step | Action | Expected Outcome | Pass/Fail | Notes |
| :--- | :--- | :--- | :--- | :--- |
| **1. Basic Load Test** | Select the model. Run a 50-word prompt using the default settings. | The response should generate cleanly and completely without crashing, freezing, or memory errors. | [ ] | Time taken: ______s |
| **2. Context Window Stress** | Submit a very long input (e.g., a pasted article > 1,000 words). Prompt for summary. | The model must process the entire context without "forgetting" or truncating parts of the source text. | [ ] | Verify full processing. |
| **3. GPU Offload Confirmation** | Check the LM Studio interface's resource usage panel (if available). | Confirm that the majority of model layers/parameters are being successfully offloaded to VRAM, not relying solely on system RAM. | [ ] | *Check console logs.* |
| **4. Temperature & Top-P Tuning** | Change `Temperature` and `Top-P` settings manually (e.g., set Temp=0.7). Run a prompt. | The model output must immediately reflect the change in parameters, showing variability as expected. | [ ] | Test parameter sensitivity. |

### 📝 Phase 2: Functional & Workflow Testing

**Objective:** Validate that the local setup can perform tasks relevant to team workflows (e.g., coding, summarizing specific data types). *Repeat this phase with at least two different models.*

| Task Category | Input Prompt/Data | Expected Behavior | Pass/Fail | Notes |
| :--- | :--- | :--- | :--- | :--- |
| **Summarization** | Paste a technical document (e.g., meeting minutes, API specs). *Prompt: "Provide three bullet points summarizing the key decisions."* | The output must be concise, accurate, and directly address the prompt's scope without hallucination or irrelevant fluff. | [ ] | Check for factual accuracy. |
| **Code Generation** | Provide a function description (e.g., "Write a Python function to reverse a dictionary"). *Prompt: "Generate only the code block."* | The model must output syntactically correct, runnable code that matches the required language and functionality. | [ ] | Run the code! |
| **Role-Playing/Tone** | Define an explicit persona (e.g., "You are a cynical senior developer."). *Prompt: "Review this commit message."* | The model must maintain the defined tone and adopt the specified role throughout its entire response. | [ ] | Consistency check. |
| **Handling Failure** | Intentionally input ambiguous or contradictory data (e.g., conflicting dates, incomplete instructions). | The model should not hallucinate an answer but instead request clarification or state its assumptions clearly. | [ ] | *Crucial safety check.* |

### 🛑 Phase 3: Troubleshooting & Sign-off

If any test failed in Phase 1 or Phase 2, immediately follow the appropriate troubleshooting guide and retest until success is achieved.

#### 🛠️ Common Issues & Fixes

| Symptom | Potential Cause | Quick Fix / Action |
| :--- | :--- | :--- |
| **"Out of Memory" Error** | Model is too large for available VRAM, or multiple apps are running. | Reduce context size (use quantization); Close background applications; Try a smaller model variant (e.g., 7B instead of 13B). |
| **Slow Generation Rate** | CPU fallback or insufficient GPU utilization. | Ensure GPU drivers are current; Check resource usage to confirm VRAM is actively being utilized by LM Studio. |
| **Inaccurate/Repetitive Output** | Model weights are corrupted, or the prompt structure is too vague. | Use a different model base; Add explicit formatting rules to your system prompt (e.g., "Respond only in JSON format."). |

#### ✅ Final Sign-Off

*   **Date Validated:** ____________________
*   **Tested By:** ____________________
*   **Model Base Used:** ____________________
*   **Result:** [ ] **PASS.** The setup is stable and functionally validated for team use.
*   **Sign-off Approver (Team Lead):** ____________________
