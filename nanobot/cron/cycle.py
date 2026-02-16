"""Cycle manager for 24-hour development coordination."""

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from nanobot.agent.loop import AgentLoop
from nanobot.bus.queue import MessageBus
from loguru import logger

async def run_cycle_check(workspace: Path):
    """
    Run the 24-hour cycle check.
    
    This script is intended to be called by the CronService or manually.
    It injects a system message into the Main Agent's loop to trigger a review
    of the project state.
    """
    
    # 1. Read Project State
    project_file = workspace / "PROJECT.md"
    if not project_file.exists():
        logger.warning(f"PROJECT.md not found at {project_file}")
        return

    # 2. Construct Prompt
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    prompt = f"""[System Notification: 24-Hour Cycle Check]

Current Time: {now}

It is time to review the project state and coordinate the next steps.
Please read 'workspace/PROJECT.md' to understand the current status.

If there are active tasks:
- Check if they are completed (by spawning a reviewer or checking files).
- If completed, mark them as done in PROJECT.md and move to the next task.
- If not started, spawn a Developer agent to begin.

If there are no active tasks:
- Review the Backlog in PROJECT.md.
- Select the next high-priority item and move it to Active Tasks.
- Start the task.

Report your decisions and actions.
"""

    # 3. Inject Message (Simulate via CLI/Direct channel for now)
    # Since we can't easily attach to a running loop from a separate process without IPC,
    # we will rely on the CronService's internal mechanism if this is run internally,
    # OR if run externally, we might need to append to a specific file that the agent watches,
    # BUT the best way given current architecture is to use the `nanobot-cli` if available,
    # or import the necessary components if running in the same process.
    
    # However, this script seems to be designed to be run as a standalone task.
    # If run standalone, it needs to spin up an agent or connect to one.
    # The CronService in `loop.py` executes jobs by calling `on_job`.
    # The `on_job` in `loop.py` (not shown but implied) hopefully routes to `process_direct`.
    
    # Actually, `CronService` in `loop.py` doesn't strictly have an `on_job` attached in `__init__`.
    # Let's look at `loop.py` again. It registers `CronTool`.
    # If we want this to be automatic, we should add a job to `cron/jobs.json` that 
    # sends a message to the agent.
    
    # The CronService supports a "payload" with "message".
    # So we don't strictly need this python script IF the cron job can just send the message.
    # BUT, if we want dynamic logic (like checking if PROJECT.md exists first), we need code.
    
    # For now, let's keep this simple:
    # We will just print the prompt. The caller (CronService via ExecTool or internal)
    # can capture it.
    
    print(prompt)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python cycle.py <workspace_path>")
        sys.exit(1)
    
    ws = Path(sys.argv[1])
    asyncio.run(run_cycle_check(ws))
