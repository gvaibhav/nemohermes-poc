# Jules Task: Checker - Audit & Verify NemoClaw Hermes Agent Deployment & SKILL.md PoC

## Context & Objective
You are acting as the **Checker** agent in a Maker-Checker pair. Your objective is to audit, test, and verify the NemoClaw Hermes deployment, Gemini API integration, and the **Toil Reduction via SKILL.md** PoC created by the Maker.

---

## Verification & Audit Steps for Checker (Jules)

### Audit 1: Environment & Sandbox Verification
1. Verify Docker Desktop engine status and OpenShell sandbox health:
   ```bash
   docker ps
   nemoclaw status
   ```
2. Verify Gemini API connectivity:
   - Ensure `GEMINI_API_KEY` is loaded securely outside git control.
   - Confirm `nemohermes` responds cleanly without authentication errors.

### Audit 2: Security & Secret Protection
1. Inspect git status and commit history (`git status`, `git log -p`) to ensure `GEMINI_API_KEY` or personal credentials are NOT present in any file or log.
2. Confirm OpenShell filesystem sandbox boundaries prevent unauthorized host modifications.

### Audit 3: Verification of PoC (SKILL.md Self-Evolving Runbook)
1. Run automated test suite:
   ```bash
   python3 -m unittest discover -s tests
   ```
2. Run end-to-end PoC script:
   ```bash
   python3 usecases/poc_toil_reduction_skill.py
   ```
3. Audit the 3 PoC Milestones:
   - **Milestone A**: Confirm rogue process (`bash -c 'while true; do echo "leak" > /dev/null; done' &`) was detected by `ps aux` and killed via `kill -9`.
   - **Milestone B**: Inspect generated `skills/cpu_sweep/SKILL.md`. Verify it contains the trigger phrase `"Run the standard CPU sweep"` and exact bash commands.
   - **Milestone C**: Confirm fresh session invocation of `"Run the standard CPU sweep"` successfully executes the runbook directly without re-reasoning.

### Audit 4: Report Generation
Generate `CHECKER_REPORT.md` summarizing:
- Gemini API & Docker Desktop integration health.
- Security Audit (Zero secret leaks, Landlock policy verification).
- Pass/Fail status of SKILL.md PoC.

---

## Deliverables Checklist
- [ ] Verified Docker Desktop and OpenShell container status.
- [ ] Validated Gemini API integration and secret isolation.
- [ ] Verified `SKILL.md` creation and structure.
- [ ] Validated fresh session execution of "Run the standard CPU sweep".
- [ ] Created `CHECKER_REPORT.md`.
