# Jules Task: Maker — Build NemoHermes (NemoClaw + Hermes + Gemini)

## Role
You are the **Maker** agent in a Maker-Checker pair. Your job is to **build, enhance, and test** the NemoHermes project — a sandboxed Hermes Agent running inside NVIDIA OpenShell on macOS with Google Gemini API.

## Context
- **Repository**: You are working inside the `nemohermes` repo. Read [`AGENTS.md`](../AGENTS.md) first for coding conventions, project structure, and rules.
- **Architecture**: Read [`IMPLEMENTATION_PLAN.md`](../IMPLEMENTATION_PLAN.md) for the full system design, component diagrams, and PoC sequence.
- **LLM Provider**: Google Gemini API via `GEMINI_API_KEY` (env var or `config/credentials.env`).
- **Upstream Source**: NVIDIA NemoClaw — https://github.com/NVIDIA/nemoclaw
- **Upstream Docs**: https://docs.nvidia.com/nemoclaw/user-guide/openclaw/home

---

## Phase 1: Environment Validation

### 1.1 Run the setup script
```bash
bash scripts/setup_nemoclaw.sh
```
This verifies Docker Desktop, Python 3.10+, installs pip deps, and clones NemoClaw source.

### 1.2 Verify existing scaffolding runs
```bash
python3 usecases/poc_toil_reduction_skill.py
python3 -m unittest discover -s tests -v
```
Both must exit 0. If they fail, fix any environment issues first.

### 1.3 Ensure package markers exist
Create `__init__.py` in both `usecases/` and `tests/` if they don't exist:
```bash
touch usecases/__init__.py tests/__init__.py
```

---

## Phase 2: Enhance the PoC Runner

The existing `usecases/poc_toil_reduction_skill.py` is a simulation harness. Enhance it to integrate with the **actual Hermes agent** via the Gemini API:

### 2.1 Add Gemini API Client
Create `usecases/gemini_client.py`:
- Load `GEMINI_API_KEY` from env or `config/credentials.env` (use `python-dotenv`)
- Initialize `google.genai.Client` with model `gemini-2.5-flash`
- Provide a `send_prompt(prompt: str, context: list[dict]) -> str` function
- Handle auth errors gracefully with clear error messages

### 2.2 Wire Hermes Turns to Real LLM
Update `poc_toil_reduction_skill.py` to optionally call the real Gemini API:
- Add a `--live` CLI flag: when set, send prompts to Gemini and parse tool-call responses
- When `--live` is not set, keep the existing deterministic simulation (default, safe for CI)
- Parse Gemini's response for bash commands (code blocks) and execute them via `subprocess`

### 2.3 Enhance SKILL.md Generation
In Turn 2, when in `--live` mode:
- Let Gemini generate the SKILL.md content based on the conversation history
- Validate the generated YAML frontmatter with `yaml.safe_load()` before writing
- If validation fails, fall back to the hardcoded template

---

## Phase 3: Expand the Test Suite

### 3.1 Add unit tests for `gemini_client.py`
Create `tests/test_gemini_client.py`:
- Mock `google.genai.Client` using `unittest.mock.patch`
- Test successful prompt/response cycle
- Test `GEMINI_API_KEY` missing → clear error
- Test auth failure → graceful handling

### 3.2 Add SKILL.md structural validation tests
Add to `tests/test_poc_skill.py`:
- Test that YAML frontmatter has all required fields (`name`, `version`, `triggers`, `description`, `author`)
- Test that `triggers` is a non-empty list of strings
- Test that Markdown body contains `## Action Sequence` with at least one fenced bash block
- Test that `parse_skill_triggers()` returns `[]` for malformed YAML

### 3.3 Add end-to-end test
Add `tests/test_e2e.py`:
- Run `python3 usecases/poc_toil_reduction_skill.py` as a subprocess
- Assert exit code 0
- Assert `skills/cpu_sweep/SKILL.md` exists and is valid
- Assert no orphan bash processes remain (`ps aux | grep "while true"`)

---

## Phase 4: Documentation Deliverables

Jules must produce or update the following documentation files. Each is a **required deliverable**.

### 4.1 Update `README.md` — Onboarding Guide
This is the primary onboarding document for new users. Ensure it contains:
- **Prerequisites** checklist (macOS, Docker Desktop, Python 3.10+, Gemini API key)
- **Step-by-step setup** from `git clone` to first PoC run
- **Repository structure** tree reflecting all new files (`gemini_client.py`, `__init__.py`, etc.)
- **Usage examples**: running in simulation mode vs `--live` mode
- **Troubleshooting** section covering at least:
  - Docker Desktop not running
  - `GEMINI_API_KEY` not set or invalid
  - Orphan processes after a crash
  - `ModuleNotFoundError` (missing `__init__.py`)

### 4.2 Create `docs/DESIGN.md` — Usecase Design Document
Create a new file `docs/DESIGN.md` documenting the PoC usecase:
- **Problem statement**: What is "toil" and why is a living runbook valuable
- **Solution overview**: 3-turn interaction pattern (diagnose → codify → replay)
- **SKILL.md format specification**: YAML frontmatter schema, required fields, trigger matching logic
- **Architecture decisions**: Why `pathlib` over `os.path`, why `signal.SIGKILL` over raw 9, why `yaml.safe_load()`
- **Extension points**: How to add new skills beyond cpu_sweep

### 4.3 Create `docs/OPERATIONS.md` — Operations Guide
Create a new file `docs/OPERATIONS.md` as a runbook for operating the agent:
- **Starting the sandbox**: How to launch the OpenShell container
- **Running the agent**: `nemohermes` commands and CLI flags
- **Managing skills**: How to list, inspect, and delete SKILL.md files
- **Monitoring**: Where to find logs, how to check sandbox health
- **Teardown**: How to stop the container, clean up processes, remove sandbox snapshots
- **Disaster recovery**: What to do if the agent spawns a runaway process, how to force-kill all agent processes

### 4.4 Update `AGENTS.md`
- Add `gemini_client.py`, `docs/DESIGN.md`, `docs/OPERATIONS.md` to the file listing
- Add any new coding conventions discovered during build

### 4.5 Verify no secrets committed
```bash
git grep -i "api_key\|secret\|token\|password" -- ':!*.example' ':!*.md' ':!*.yaml'
```
This must return empty. If it finds anything, remove it before committing.

---

## Deliverables Checklist

### Code
- [ ] `usecases/__init__.py` and `tests/__init__.py` exist
- [ ] `usecases/gemini_client.py` created with Gemini API wrapper
- [ ] `usecases/poc_toil_reduction_skill.py` enhanced with `--live` flag
- [ ] `tests/test_gemini_client.py` created (mocked Gemini tests)
- [ ] `tests/test_poc_skill.py` expanded with SKILL.md validation tests
- [ ] `tests/test_e2e.py` created (subprocess end-to-end test)

### Tests
- [ ] All tests pass: `python3 -m unittest discover -s tests -v`
- [ ] PoC runs clean: `python3 usecases/poc_toil_reduction_skill.py` exits 0
- [ ] No orphan processes after PoC run

### Documentation
- [ ] `README.md` updated with full onboarding guide and troubleshooting
- [ ] `docs/DESIGN.md` created with usecase design and SKILL.md spec
- [ ] `docs/OPERATIONS.md` created with operations runbook
- [ ] `AGENTS.md` updated with new files and conventions

### Security
- [ ] No secrets in git: `git grep -i api_key` returns empty
- [ ] PR opened with clear description of changes

---

## Quality Gates (Must Pass Before PR)

```bash
# 1. All tests green
python3 -m unittest discover -s tests -v

# 2. PoC simulation mode
python3 usecases/poc_toil_reduction_skill.py

# 3. No orphan processes
ps aux | grep "while true" | grep -v grep | wc -l  # must be 0

# 4. No secrets committed
git diff --cached | grep -i "api_key\|gemini.*=\|secret\|token" | wc -l  # must be 0

# 5. SKILL.md is valid YAML frontmatter
python3 -c "import yaml; from pathlib import Path; d=Path('skills/cpu_sweep/SKILL.md').read_text().split('---',2); yaml.safe_load(d[1]); print('✓ valid')"
```
