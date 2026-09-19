# Usecase Design Document: Toil Reduction via SKILL.md

## Problem Statement
"Toil" in SRE encompasses repetitive, manual tasks like diagnosing memory leaks or runaway CPU processes. A living runbook reduces this toil by codifying these steps into an automated asset that evolves as systems change.

## Solution Overview
We utilize a 3-turn interaction pattern to codify tribal knowledge into actionable automation:
1. **Diagnose**: Identify the rogue problem via standard CLI tools.
2. **Codify**: Generate a standardized `SKILL.md` utilizing Gemini that packages the diagnostic process into a runnable module.
3. **Replay**: In a fresh context, immediately execute the codified skill rather than re-evaluating the problem from scratch.

## SKILL.md Format Specification
A generated skill encapsulates metadata in YAML frontmatter followed by a markdown body.
Required Frontmatter Fields:
- `name`: Identifier of the skill.
- `version`: Version string.
- `description`: Human-readable goal of the skill.
- `triggers`: A non-empty list of string phrases that invoke this skill.
- `author`: Origin of the skill (e.g. `hermes-agent`).

The Markdown body must include an `## Action Sequence` header and at least one fenced bash block (````bash ... ````).

## Architecture Decisions
- **`pathlib` over `os.path`**: Provides cross-platform, object-oriented path traversal, avoiding string manipulation bugs.
- **`signal.SIGKILL` over raw 9**: Constant mapping improves code readability and cross-platform reliability.
- **`yaml.safe_load()`**: Safeguards against arbitrary object instantiation during YAML parsing.

## Extension Points
New skills can be dynamically learned or explicitly authored into `skills/<new_skill>/SKILL.md`. By registering triggers, the agent can expand its runbook database infinitely.
