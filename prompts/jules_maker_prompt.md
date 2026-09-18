# Jules Task: Maker - Provision NemoClaw with Hermes Agent (Gemini LLM) & Build SKILL.md PoC

## Context & Objective
You are acting as the **Maker** agent in a Maker-Checker pair. Your objective is to clone the NVIDIA NemoClaw repository (`https://github.com/NVIDIA/nemoclaw`), set up NVIDIA OpenShell governance runtime on macOS (using Docker Desktop), configure the **Hermes Agent** (`nemohermes`) using the **Gemini API** (`GEMINI_API_KEY`), and build an end-to-end PoC demonstrating **Toil Reduction via SKILL.md (Self-Evolving Runbooks)** inside an OpenShell container.

## Environment & Prerequisites
- Host OS: macOS with Docker Desktop installed.
- Repository: https://github.com/NVIDIA/nemoclaw
- LLM Provider: Google Gemini API via `GEMINI_API_KEY` (Google AI Studio / AI Pro subscription).
- Documentation: https://docs.nvidia.com/nemoclaw/user-guide/openclaw/home

---

## Task Instructions for Maker (Jules)

### Step 1: Repository & Environment Setup
1. Clone `https://github.com/NVIDIA/nemoclaw.git` into the workspace directory.
2. Verify Python 3.10+ and Docker Desktop (`docker info`) are running.

### Step 2: NemoClaw & Hermes Installation with Gemini LLM
1. Initialize NemoClaw & OpenShell with Hermes agent:
   ```bash
   curl -fsSL https://www.nvidia.com/nemoclaw.sh | NEMOCLAW_AGENT=hermes NEMOCLAW_SANDBOX_NAME=mac-hermes-agent bash
   ```
2. Configure `~/.nemoclaw/config.yaml` and credentials for Gemini LLM:
   ```env
   NEMOCLAW_LLM_PROVIDER=gemini
   GEMINI_API_KEY=<USER_GEMINI_API_KEY>
   ```
3. Verify status and Hermes CLI:
   ```bash
   nemoclaw status
   nemohermes --version
   ```

### Step 3: Implement PoC - Toil Reduction via SKILL.md (Self-Evolving Runbook)

Create a runnable test harness script `usecases/poc_toil_reduction_skill.py` and supporting setup:

#### 1. Mock Setup
Start a background rogue process inside the OpenShell sandbox container:
```bash
bash -c 'while true; do echo "leak" > /dev/null; done' &
```

#### 2. Interactive Sequence Simulation
Implement an automated runner that simulates the following prompt sequence with `nemohermes`:

- **Turn 1: Diagnostic & Process Termination**
  - **Prompt**: `"The system feels sluggish. Find the process consuming the most CPU and terminate it."`
  - **Expected Action**: Hermes runs `ps aux --sort=-%cpu | head -n 5`, identifies the rogue bash process PID, and executes `kill -9 <PID>`.

- **Turn 2: Skill Codification**
  - **Prompt**: `"Good job. Whenever I say 'Run the standard CPU sweep', I want you to perform exactly that diagnostic and cleanup process. Save this to your skills."`
  - **Expected Action**: Hermes creates or updates a `skills/cpu_sweep/SKILL.md` file detailing the command sequence and trigger phrase `"Run the standard CPU sweep"`.

- **Turn 3: Verification in Fresh Context Window**
  - Spawn a background leak again: `bash -c 'while true; do echo "leak" > /dev/null; done' &`
  - Reset / start a fresh session window of Hermes.
  - **Prompt**: `"Run the standard CPU sweep."`
  - **Expected Action**: Hermes detects the trigger in `SKILL.md`, bypasses re-reasoning, and immediately executes the codified diagnostic & cleanup bash sequence.

### Step 4: Test Suite & Automation
1. Create `tests/test_poc_skill.py` to automate end-to-end execution of Turn 1, Turn 2, and Turn 3.
2. Provide a clear `README.md` explaining how to execute the PoC script and inspect the generated `SKILL.md`.

---

## Deliverables Checklist
- [ ] Cloned `NVIDIA/nemoclaw` repo.
- [ ] Configured `nemohermes` with `GEMINI_API_KEY` on Docker Desktop.
- [ ] Created `usecases/poc_toil_reduction_skill.py` implementing the rogue loop setup and 3-turn sequence.
- [ ] Verified `SKILL.md` generation and skill activation in a fresh session.
- [ ] Created automated test in `tests/test_poc_skill.py` and `README.md`.
