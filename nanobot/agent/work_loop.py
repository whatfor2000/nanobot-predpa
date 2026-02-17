
import asyncio
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

from loguru import logger

from nanobot.agent.task import TaskBoard
from nanobot.agent.agent import Agent
from nanobot.bus.queue import MessageBus
from nanobot.bus.events import InboundMessage
from nanobot.providers.base import LLMProvider
from nanobot.agent.roles import AgentRole


class WorkLoop:
    """
    Endless work loop for autonomous agent operation.
    
    Continuously:
    - Checks TaskBoard for todo tasks
    - Processes tasks via Manager agent
    - Checks HEARTBEAT.md for periodic tasks
    """
    
    def __init__(
        self,
        workspace: Path,
        provider: LLMProvider,
        bus: MessageBus,
        sleep_interval: int = 300,  # 5 minutes
        heartbeat_interval: int = 1800,  # 30 minutes
    ):
        self.workspace = workspace
        self.provider = provider
        self.bus = bus
        self.sleep_interval = sleep_interval
        self.heartbeat_interval = heartbeat_interval
        
        # Components
        self.task_board = TaskBoard(workspace)
        self.manager = Agent(
            role=AgentRole.MANAGER,
            workspace=workspace,
            bus=bus,
            provider=provider
        )
        
        # State
        self.last_heartbeat_check = datetime.now()
        self._running = False
        
    async def start(self):
        """Start the endless work loop."""
        logger.info("Starting WorkLoop...")
        self._running = True
        
        await self.manager.start()
        
        while self._running:
            try:
                await self._run_cycle()
                logger.info(f"Cycle complete. Sleeping for {self.sleep_interval}s...")
                await asyncio.sleep(self.sleep_interval)
            except KeyboardInterrupt:
                logger.info("WorkLoop interrupted by user")
                break
            except Exception as e:
                logger.error(f"Error in work loop: {e}")
                await asyncio.sleep(self.sleep_interval)
    
    async def _run_cycle(self):
        """Run a single work cycle."""
        logger.info("--- Work Cycle Start ---")
        
        # 1. Check for todo tasks
        todo_tasks = self.task_board.list_tasks(status="todo")
        
        if todo_tasks:
            logger.info(f"Found {len(todo_tasks)} todo tasks")
            for task in todo_tasks:
                await self._process_task(task)
        else:
            logger.info("No todo tasks found")
        
        # 2. Check HEARTBEAT.md if interval elapsed
        if self._should_check_heartbeat():
            await self._check_heartbeat()
            self.last_heartbeat_check = datetime.now()
        
        logger.info("--- Work Cycle End ---")
    
    async def _process_task(self, task):
        """Process a single task via Manager."""
        logger.info(f"Processing task: {task.id} - {task.title}")
        
        # Update status to in_progress
        self.task_board.update_task(task.id, status="in_progress")
        
        # Create message for Manager
        message_content = f"""Task: {task.title}
Description: {task.description}
Assignee: {task.assignee or 'unassigned'}

Please process this task."""
        
        msg = InboundMessage(
            channel=f"agent:{AgentRole.MANAGER.value}",
            chat_id="work_loop",
            sender_id="work_loop",
            content=message_content
        )
        
        # Process via Manager
        response = await self.manager.process_message(msg)
        
        if response:
            logger.info(f"Manager response: {response.content[:100]}...")
        
        # Note: Manager should update task status via TaskTool
        # We don't auto-complete here
    
    def _should_check_heartbeat(self) -> bool:
        """Check if heartbeat interval has elapsed."""
        elapsed = (datetime.now() - self.last_heartbeat_check).total_seconds()
        return elapsed >= self.heartbeat_interval
    
    async def _check_heartbeat(self):
        """Check HEARTBEAT.md for periodic tasks."""
        heartbeat_file = self.workspace / "HEARTBEAT.md"
        
        if not heartbeat_file.exists():
            logger.info("HEARTBEAT.md not found, skipping")
            return
        
        content = heartbeat_file.read_text(encoding="utf-8")
        
        # Extract tasks from "Active Tasks" section
        if "## Active Tasks" not in content:
            logger.info("No Active Tasks section in HEARTBEAT.md")
            return
        
        # Simple extraction: lines after "## Active Tasks" and before next "##"
        lines = content.split("\n")
        in_active = False
        tasks = []
        
        for line in lines:
            if "## Active Tasks" in line:
                in_active = True
                continue
            if in_active and line.strip().startswith("##"):
                break
            if in_active and line.strip() and not line.strip().startswith("<!--"):
                tasks.append(line.strip())
        
        if not tasks:
            logger.info("No active tasks in HEARTBEAT.md")
            return
        
        logger.info(f"Found {len(tasks)} heartbeat tasks")
        
        # Send to Manager
        heartbeat_message = f"""HEARTBEAT CHECK

The following periodic tasks need attention:

{chr(10).join(tasks)}

Please review and process these tasks."""
        
        msg = InboundMessage(
            channel=f"agent:{AgentRole.MANAGER.value}",
            chat_id="heartbeat",
            sender_id="heartbeat",
            content=heartbeat_message
        )
        
        response = await self.manager.process_message(msg)
        
        if response:
            logger.info(f"Heartbeat response: {response.content[:100]}...")
    
    def stop(self):
        """Stop the work loop."""
        logger.info("Stopping WorkLoop...")
        self._running = False
