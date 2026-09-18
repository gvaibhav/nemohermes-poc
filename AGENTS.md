# AGENTS.md - Instructions for Autonomous Coding Agents (Jules)

Welcome, Agent! This repository contains the reference implementation and PoC for running **NVIDIA NemoClaw** with a **Hermes Agent (`nemohermes`)** on macOS/Docker using **Google Gemini API**.

---

## Project Context & Architecture

- **Project Name**: NemoHermes
- **Sandboxing Engine**: NVIDIA OpenShell (Docker runtime)
- **LLM Engine**: Google Gemini API via `GEMINI_API_KEY`
- **Primary Usecase**: Toil Reduction via `SKILL.md` (Self-Evolving Runbooks)

---

## Workspace Setup Instructions for Jules

1. **Environment Setup**:
   Execute the setup script to verify Docker and pull source dependencies:
   ```bash
   bash scripts/setup_nemoclaw.sh
   ```

2. **Credentials Configuration**:
   Ensure `GEMINI_API_KEY` is set in the environment or in `config/credentials.env` (do NOT commit secrets to git).

3. **Running the PoC**:
   To execute the 3-turn SKILL.md PoC runner:
   ```bash
   python3 usecases/poc_toil_reduction_skill.py
   ```

4. **Running Tests**:
   To execute the automated unit test suite:
   ```bash
   python3 -m unittest discover -s tests
   ```

---

## Maker-Checker Delegation Tasks

- **Maker Prompt**: Follow the instructions in `prompts/jules_maker_prompt.md`.
- **Checker Prompt**: Follow the audit instructions in `prompts/jules_checker_prompt.md`.
- **Pull Request Guidelines**:
  - Always verify that all tests pass (`python3 -m unittest discover -s tests`) before submitting a PR.
  - Never commit `.env` or `credentials.env` files.
