# NemoHermes: Sandboxed Hermes Agent on macOS via NVIDIA NemoClaw

This repository contains the scaffolding, configuration, setup scripts, and PoC usecases for running a **Hermes Agent** (`nemohermes`) inside an **NVIDIA OpenShell** sandbox on macOS (using Docker Desktop) powered by **Google Gemini API**.

---

## Repository Structure

```
nemohermes/
├── IMPLEMENTATION_PLAN.md      # Detailed architecture & implementation plan
├── README.md                   # Workspace overview & setup instructions
├── requirements.txt            # Python dependencies
├── config/
│   ├── credentials.env.example # Environment variable template for GEMINI_API_KEY
│   └── nemoclaw_config.yaml    # NemoClaw sandbox & agent configuration template
├── prompts/
│   ├── jules_maker_prompt.md   # Task specification for Jules (Maker Agent)
│   └── jules_checker_prompt.md # Audit specification for Jules (Checker Agent)
├── scripts/
│   └── setup_nemoclaw.sh       # Automated installation and onboarding script
├── usecases/
│   └── poc_toil_reduction_skill.py # Self-Evolving Runbooks (SKILL.md) PoC
├── skills/
│   └── .gitkeep                # Directory for codified Hermes skills
└── tests/
    └── test_poc_skill.py       # Automated integration tests for the PoC
```

---

## Quickstart

### 1. Prerequisites
- **macOS** with **Docker Desktop** installed and running.
- **Python 3.10+**.
- **Google Gemini API Key** (from Google AI Studio / Google AI Pro subscription).

### 2. Configuration
Copy the credentials template and add your Gemini API key:
```bash
cp config/credentials.env.example config/credentials.env
# Edit config/credentials.env and insert your GEMINI_API_KEY
```

### 3. Setup NemoClaw & Hermes Sandbox
Run the setup script to install NemoClaw and initialize the OpenShell container:
```bash
bash scripts/setup_nemoclaw.sh
```

### 4. Run the PoC (Toil Reduction via SKILL.md)
Execute the PoC script to run the 3-turn sequence:
```bash
python3 usecases/poc_toil_reduction_skill.py
```

### 5. Delegation to Jules (`jules.google.com`)
- Use `prompts/jules_maker_prompt.md` to instruct the **Maker** agent in Jules.
- Use `prompts/jules_checker_prompt.md` to instruct the **Checker** agent in Jules.
