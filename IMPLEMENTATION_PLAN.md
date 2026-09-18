# NemoClaw Hermes Agent Deployment & Maker-Checker Execution Plan for Jules

This plan details the setup of **NVIDIA NemoClaw** with a **Hermes Agent** on macOS using **Docker Desktop** and **Google Gemini API**, along with a structured **Maker-Checker Combo** tailored for delegation to `jules.google.com`.

## Configuration Overview

- **Host OS**: macOS
- **Container Engine**: Docker Desktop
- **LLM Provider**: Google Gemini API via `GEMINI_API_KEY` (Google AI Studio / Google AI Pro subscription)
- **Primary Usecase / PoC**: *Toil Reduction via SKILL.md (Self-Evolving Runbooks)*

---

## PoC Architecture: Toil Reduction via SKILL.md

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Hermes as Hermes Agent (nemohermes)
    participant OS as OpenShell Container
    participant Skill as SKILL.md Store

    Note over OS: Rogue process started: bash while true; do leak...
    User->>Hermes: "The system feels sluggish. Find process consuming most CPU and terminate it."
    Hermes->>OS: Executes ps aux --sort=-%cpu | head -n 5
    OS-->>Hermes: Returns PID & process info
    Hermes->>OS: Executes kill -9 <PID>
    
    User->>Hermes: "Good job. Whenever I say 'Run standard CPU sweep', save this to your skills."
    Hermes->>Skill: Codifies command sequence into SKILL.md
    
    Note over Hermes: Session Closed / Context Window Reset
    Note over OS: Rogue process started again
    
    User->>Hermes: "Run the standard CPU sweep."
    Hermes->>Skill: Reads SKILL.md trigger
    Hermes->>OS: Immediately executes codified kill sequence (Bypasses Re-reasoning)
```

---

## Maker-Checker Combo Specification for Jules

### 1. Maker Specification (`prompts/jules_maker_prompt.md`)
The **Maker** prompt instructs Jules to set up environment, clone repo, install NemoClaw & Hermes with Gemini API credentials, configure OpenShell sandbox in Docker Desktop, and implement the **Toil Reduction via SKILL.md** PoC script and test suite.

- **Step 1: Environment & Repository Setup**
  - Clone `https://github.com/NVIDIA/nemoclaw.git`.
  - Verify Docker Desktop and Python 3.10+.
- **Step 2: NemoClaw & Hermes Installation**
  - Run onboarding CLI: `NEMOCLAW_AGENT=hermes NEMOCLAW_SANDBOX_NAME=mac-hermes-agent`.
  - Configure `GEMINI_API_KEY` for Google Gemini model access.
- **Step 3: PoC Implementation**
  - Create rogue process simulation in OpenShell container.
  - Automate Turn 1 (Diagnostic & Kill), Turn 2 (SKILL.md codification), and Turn 3 (Fresh session execution of `"Run the standard CPU sweep"`).

### 2. Checker Specification (`prompts/jules_checker_prompt.md`)
The **Checker** prompt instructs Jules to review, test, audit security policies, and verify execution logs of the Maker's output.

- **Check 1: Environment & Gemini API Audit**
  - Verify Docker Desktop container status and `nemoclaw status`.
  - Ensure `GEMINI_API_KEY` is kept secure and out of git repository.
- **Check 2: PoC Milestone Verification**
  - Verify Turn 1 process termination.
  - Verify Turn 2 `skills/cpu_sweep/SKILL.md` content and formatting.
  - Verify Turn 3 instant execution without re-reasoning in a fresh context window.
- **Check 3: Report Generation**
  - Generate `CHECKER_REPORT.md`.

---

## Verification Plan

### Automated Tests
- Verification of NemoClaw sandbox status: `nemoclaw status`
- Execution of Maker test suite against Hermes agent: `python3 -m unittest discover -s tests`

### Manual Verification
- Invoking `poc_toil_reduction_skill.py` and reviewing generated `SKILL.md`.
