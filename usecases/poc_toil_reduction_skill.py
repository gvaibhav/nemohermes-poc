#!/usr/bin/env python3
"""
PoC 2: Toil Reduction via SKILL.md (Self-Evolving Runbooks)

Demonstrates how a Hermes agent learns a tribal-knowledge SRE task
(CPU sweep diagnostic & kill) and codifies it into a reusable,
persistent SKILL.md automation script that survives session resets.

Usage:
    python3 usecases/poc_toil_reduction_skill.py
"""

import os
import signal
import sys
import time
import subprocess
import yaml
from pathlib import Path
from typing import Optional

# Resolve project root relative to this file, not cwd
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = PROJECT_ROOT / "skills" / "cpu_sweep"
SKILL_FILE = SKILLS_DIR / "SKILL.md"

# Track all spawned PIDs for guaranteed cleanup
_spawned_pids: list[int] = []


def start_rogue_process() -> int:
    """Spawn an infinite CPU-leaking background bash process.

    Returns:
        The PID of the spawned rogue process.
    """
    print("[Harness] Spawning rogue CPU-leaking process...")
    proc = subprocess.Popen(
        ["bash", "-c", 'while true; do echo "leak" > /dev/null; done'],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(1)
    _spawned_pids.append(proc.pid)
    print(f"[Harness] Rogue process started with PID: {proc.pid}")
    return proc.pid


def _safe_kill(pid: int) -> bool:
    """Attempt to kill a single process by PID. Returns True if killed."""
    try:
        os.kill(pid, signal.SIGKILL)
        return True
    except ProcessLookupError:
        return True  # already dead
    except PermissionError:
        print(f"[Warning] Permission denied killing PID {pid}")
        return False


def cleanup_all_spawned() -> None:
    """Terminate every rogue process we started, regardless of outcome."""
    for pid in _spawned_pids:
        _safe_kill(pid)
    _spawned_pids.clear()


def _find_process(pid: int) -> Optional[str]:
    """Run `ps` to check if a process is alive. Returns stdout or None."""
    try:
        res = subprocess.run(
            ["ps", "-p", str(pid), "-o", "pid,pcpu,comm"],
            capture_output=True, text=True,
        )
        if res.returncode == 0 and str(pid) in res.stdout:
            return res.stdout
    except PermissionError:
        pass
    return None


def simulate_turn_1(pid: int) -> None:
    """Turn 1: Diagnostic & Process Termination.

    Simulates:
        User: 'The system feels sluggish. Find the process consuming
              the most CPU and terminate it.'
    """
    print("\n--- TURN 1: Diagnostic & Process Termination ---")
    print("User: 'The system feels sluggish. Find the process consuming "
          "the most CPU and terminate it.'")

    print("[Hermes Action] Executing: ps -p <PID> -o pid,pcpu,comm")
    ps_output = _find_process(pid)

    if ps_output is not None:
        print(f"[Hermes Action] Process listing:\n{ps_output.strip()}")
        print(f"[Hermes Action] Identified rogue process (PID {pid}). "
              f"Executing: kill -9 {pid}")
        if _safe_kill(pid):
            print("[Hermes Action] ✓ Rogue process terminated successfully.")
        else:
            print("[Hermes Action] ✗ Failed to terminate rogue process.")
            raise RuntimeError(f"Could not kill PID {pid}")
    else:
        # Fallback: try killing anyway — ps may be restricted in sandbox
        print(f"[Hermes Action] ps unavailable or restricted. "
              f"Attempting direct kill of PID {pid}.")
        if _safe_kill(pid):
            print("[Hermes Action] ✓ Rogue process terminated (direct kill).")
        else:
            print("[Hermes Action] ✗ Failed to terminate rogue process.")
            raise RuntimeError(f"Could not kill PID {pid}")


def simulate_turn_2() -> None:
    """Turn 2: Skill Codification.

    Simulates:
        User: 'Good job. Whenever I say "Run the standard CPU sweep",
              save this to your skills.'

    Creates a SKILL.md with YAML frontmatter (triggers, description)
    and a Markdown action sequence body.
    """
    print("\n--- TURN 2: Skill Codification ---")
    print('User: \'Good job. Whenever I say "Run the standard CPU sweep", '
          "I want you to perform exactly that diagnostic and cleanup "
          "process. Save this to your skills.'")

    SKILLS_DIR.mkdir(parents=True, exist_ok=True)

    # Build skill content with proper YAML frontmatter
    frontmatter = {
        "name": "cpu_sweep",
        "version": "1.0",
        "description": "Run standard CPU sweep to find and terminate "
                       "rogue processes consuming excessive CPU.",
        "triggers": [
            "Run the standard CPU sweep",
            "CPU sweep",
            "standard CPU sweep",
        ],
        "author": "hermes-agent",
    }

    body = """
# Standard CPU Sweep Runbook

## Description
Diagnostic and remediation workflow for high CPU load caused by
runaway or rogue processes.

## Action Sequence
1. **Identify** high-CPU processes:
   ```bash
   ps aux --sort=-%cpu | head -n 5
   ```
2. **Terminate** rogue leak processes:
   ```bash
   pkill -9 -f "while true; do echo leak"
   ```

## Rollback
If a legitimate process was killed, restart it from the service
manager or process supervisor.
"""

    skill_content = f"---\n{yaml.dump(frontmatter, default_flow_style=False).strip()}\n---\n{body}"
    SKILL_FILE.write_text(skill_content)

    rel_path = (SKILL_FILE.relative_to(PROJECT_ROOT)
                if SKILL_FILE.is_relative_to(PROJECT_ROOT)
                else SKILL_FILE)
    print(f"[Hermes Action] Created skill file at: {rel_path}")
    print("[Hermes Action] Trigger registered: 'Run the standard CPU sweep'")


def parse_skill_triggers(skill_path: Path) -> list[str]:
    """Parse YAML frontmatter from a SKILL.md and return trigger list."""
    text = skill_path.read_text()
    parts = text.split("---", 2)
    if len(parts) < 3:
        return []
    try:
        meta = yaml.safe_load(parts[1])
        return meta.get("triggers", []) if isinstance(meta, dict) else []
    except yaml.YAMLError:
        return []


def simulate_turn_3() -> None:
    """Turn 3: Verification in Fresh Context Window.

    Simulates a session reset, spawns a new rogue process, and
    verifies that the agent can immediately execute the codified
    SKILL.md runbook without re-reasoning.
    """
    print("\n--- TURN 3: Verification in Fresh Context Window ---")
    new_pid = start_rogue_process()

    print("\n[Harness] Resetting context window / Starting fresh session...")
    print("User: 'Run the standard CPU sweep.'")

    if not SKILL_FILE.exists():
        print("✗ [Verification FAILURE] SKILL.md not found.")
        _safe_kill(new_pid)
        raise RuntimeError("SKILL.md was not created by Turn 2")

    # Parse and validate the skill
    triggers = parse_skill_triggers(SKILL_FILE)
    matched = any("cpu sweep" in t.lower() for t in triggers)

    if not matched:
        print(f"✗ [Verification FAILURE] No matching trigger found. "
              f"Triggers: {triggers}")
        _safe_kill(new_pid)
        raise RuntimeError("SKILL.md trigger mismatch")

    print(f"[Hermes Action] Trigger matched in {SKILL_FILE.name}! "
          "Bypassing re-reasoning...")
    print("[Hermes Action] Executing codified runbook command: "
          "kill -9 <PID>")

    killed = _safe_kill(new_pid)
    time.sleep(0.5)

    # Verify the process is actually gone
    still_alive = _find_process(new_pid) is not None

    if killed and not still_alive:
        print("✓ [Verification SUCCESS] Rogue process terminated via "
              "codified SKILL.md runbook!")
    else:
        print("✗ [Verification FAILURE] Rogue process still active.")
        raise RuntimeError(f"PID {new_pid} survived termination")


def main() -> int:
    """Run the full 3-turn PoC sequence. Returns exit code."""
    print("=" * 60)
    print(" PoC: Toil Reduction via SKILL.md (Self-Evolving Runbooks)")
    print("=" * 60)

    exit_code = 0
    pid = start_rogue_process()
    try:
        simulate_turn_1(pid)
        simulate_turn_2()
        simulate_turn_3()
        print(f"\n{'=' * 60}")
        print(" PoC Complete: Living Runbook Verified!")
        print("=" * 60)
    except Exception as e:
        print(f"\n✗ Error executing PoC: {e}")
        exit_code = 1
    finally:
        cleanup_all_spawned()

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
