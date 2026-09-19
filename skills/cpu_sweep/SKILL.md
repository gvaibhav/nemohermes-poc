---
author: hermes-agent
description: Run standard CPU sweep to find and terminate rogue processes consuming
  excessive CPU.
name: cpu_sweep
triggers:
- Run the standard CPU sweep
- CPU sweep
- standard CPU sweep
version: '1.0'
---

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
