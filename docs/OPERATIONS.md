# Operations Guide

## Starting the Sandbox
To launch the OpenShell container, run the initial setup script which guarantees all dependencies are correctly met:
```bash
bash scripts/setup_nemoclaw.sh
```

## Running the Agent
Execute the main usecase handler:
- Simulation mode: `python3 usecases/poc_toil_reduction_skill.py`
- Live mode (Gemini Integration): `python3 usecases/poc_toil_reduction_skill.py --live`

## Managing Skills
Skills are stored persistently in the `skills/` directory.
- **List Skills**: Run `ls -R skills/`
- **Inspect**: Open the `SKILL.md` inside a specific skill folder to see its YAML frontmatter triggers and action sequences.
- **Delete**: Simply remove the folder to unlearn the skill, e.g. `rm -r skills/cpu_sweep`.

## Monitoring
- Check process execution outputs directly from the terminal console running the Hermes agent.
- Sandbox health can be verified natively by ensuring the Docker container is functioning normally via Docker Desktop logs.

## Teardown
- Ensure all loops are completed or graceful exiting.
- The Python script executes `cleanup_all_spawned()` intrinsically for gracefully reaping child loops. Stop Docker manually to halt the sandbox completely.

## Disaster Recovery
- If the agent spawns a runaway process, you can force-kill all associated leak processes safely:
```bash
pkill -9 -f "while true; do echo 'leak'"
```
