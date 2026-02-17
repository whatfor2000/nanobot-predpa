import asyncio
import uuid
from pathlib import Path
from typing import Any

from loguru import logger

from nanobot.agent.roles import AgentRole
from nanobot.bus.queue import MessageBus
from nanobot.bus.events import InboundMessage, OutboundMessage
from nanobot.agent.context import ContextBuilder
from nanobot.agent.memory import MemoryStore
from nanobot.agent.tools.registry import ToolRegistry
from nanobot.providers.base import LLMProvider
from nanobot.agent.tools.message import SendMessageTool
from nanobot.agent.task import TaskBoard
from nanobot.agent.tools.task import TaskTool

from nanobot.agent.subagent import SubagentManager
from nanobot.agent.tools.filesystem import ReadFileTool, WriteFileTool, EditFileTool, ListDirTool
from nanobot.agent.tools.web import WebSearchTool, WebFetchTool
from nanobot.agent.tools.spawn import SpawnTool
from nanobot.agent.tools.shell import ExecTool

class Agent:
    """
    Autonomous Agent entity.
    
    Each agent has:
    - A specific Role (Manager, Researcher, etc.)
    - A persistent MemoryStore (workspace/<role>/memory/)
    - A specific System Prompt (workspace/<role>/AGENT.md)
    - A MessageBus channel (agent:<role>)
    """

    def __init__(
        self,
        role: AgentRole | str,
        workspace: Path,
        bus: MessageBus,
        provider: LLMProvider,
        model: str | None = None,
    ):
        self.role = role if isinstance(role, AgentRole) else AgentRole(role)
        self.workspace = workspace
        self.bus = bus
        self.provider = provider
        self.model = model or provider.get_default_model()
        
        self.id = str(uuid.uuid4())[:8]
        self._running = False
        
        # Paths
        self.role_dir = self.workspace / self.role.value
        self.memory_dir = self.role_dir / "memory"
        self.prompt_file = self.role_dir / "AGENT.md"
        
        # Components
        self.memory = MemoryStore(self.workspace, memory_dir=self.memory_dir)
        self.context = ContextBuilder(self.workspace)
        self.tools = ToolRegistry()
        
        # Subagent Manager for this Agent
        self.subagents = SubagentManager(
            provider=provider,
            workspace=workspace,
            bus=bus,
            model=self.model,
            restrict_to_workspace=False # Agents are trusted?
        )
        
        # Task Board (shared across all agents)
        self.task_board = TaskBoard(workspace)
        
        # Tools
        self._register_tools()

    def _register_tools(self):
        """Register agent-specific tools."""
        # 1. Communication
        self.tools.register(SendMessageTool(self.bus, self.role.value))
        
        # 2. File Operations
        self.tools.register(ReadFileTool())
        self.tools.register(WriteFileTool())
        self.tools.register(EditFileTool())
        self.tools.register(ListDirTool())
        
        # 3. Web & Shell
        self.tools.register(WebSearchTool())
        self.tools.register(WebFetchTool())
        self.tools.register(ExecTool(working_dir=str(self.workspace)))
        
        # 4. Spawning
        # Agent can spawn subagents. The subagent results will come back to "agent:<role>"
        spawn_tool = SpawnTool(self.subagents)
        spawn_tool.set_context(channel=f"agent:{self.role.value}", chat_id="direct")
        self.tools.register(spawn_tool)
        
        # 5. Task Management
        self.tools.register(TaskTool(self.task_board))

    async def start(self):
        """Start the agent loop and listen for messages."""
        self._running = True
        logger.info(f"Agent [{self.role.value}] started.")
        
        # Ensure directories exist
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        if not self.prompt_file.exists():
             logger.warning(f"Agent prompt not found at {self.prompt_file}")

        # Subscribe to bus (conceptually - in reality, bus pushes to queue)
        # The main Loop dispatch mechanism needs to route to this specific instance
        # OR this Agent runs its own consume loop.
        
        # Current Architecture Limitation: 
        # The `AgentLoop` in `loop.py` consumes *all* inbound messages.
        # We need to refactor `loop.py` to route `agent:<role>` messages to this instance.
        # For now, let's assume `Agent` is a data structure used by `AgentLoop`.

    async def load_system_prompt(self, skill_names: list[str] | None = None) -> str:
        """Load the system prompt from file."""
        base_prompt = ""
        if self.prompt_file.exists():
            base_prompt = self.prompt_file.read_text(encoding="utf-8")
        else:
            base_prompt = f"You are a {self.role.value} agent."
            
        # Build full context using ContextBuilder, but override identity/bootstrap if needed specifically for this agent
        # For now, let's use a simpler prompt construction or reuse ContextBuilder if compatible
        # ContextBuilder assumes "workspace" root. 
        # We might want to construct a prompt that includes the Agent's specific context.
        
        return f"""# Agent: {self.role.value}

{base_prompt}

## Context
You are part of a Multi-Agent System.
Your memory is located at: {self.memory_dir}
"""

    async def process_message(self, msg: InboundMessage) -> OutboundMessage | None:
        """Process an inbound message directed to this agent."""
        logger.info(f"Agent [{self.role.value}] processing message from {msg.sender_id}")
        
        # Build messages
        system_prompt = await self.load_system_prompt()
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history (if we were maintaining a session per sender)
        # For simplicity, let's treat each message as a fresh task or maintain a short volatile history
        # (Implementing full session management per Agent might be overkill for now, but `self.memory` handles long-term)
        
        messages.append({"role": "user", "content": msg.content})
        
        final_content, _ = await self._run_loop(messages)
        
        return OutboundMessage(
            channel=msg.channel,
            chat_id=msg.chat_id,
           # sender_id=f"agent:{self.role.value}", # OutboundMessage doesn't have sender_id, the Bus wrapper handles it or it's implied
            content=final_content or "No response."
        )

    async def _run_loop(self, messages: list[dict[str, Any]]) -> tuple[str | None, list[str]]:
        """Run the agent execution loop."""
        iteration = 0
        final_content = None
        tools_used = []
        max_iterations = 15
        
        while iteration < max_iterations:
            iteration += 1
            
            response = await self.provider.chat(
                messages=messages,
                tools=self.tools.get_definitions(),
                model=self.model,
            )
            
            if response.has_tool_calls:
                # Add assistant message
                tool_call_dicts = [
                     {"id": tc.id, "type": "function", "function": {"name": tc.name, "arguments": tc.arguments}} # arguments dict, not string? check provider
                     for tc in response.tool_calls
                ]
                # Note: valid OpenAI format requires arguments to be string JSON
                # But our provider wrapper might return dicts. verify loop.py usage.
                # loop.py: "arguments": json.dumps(tc.arguments)
                import json
                tool_call_dicts_json = [
                     {"id": tc.id, "type": "function", "function": {"name": tc.name, "arguments": json.dumps(tc.arguments)}} 
                     for tc in response.tool_calls
                ]

                messages.append({
                    "role": "assistant",
                    "content": response.content or "",
                    "tool_calls": tool_call_dicts_json
                })
                
                for tool_call in response.tool_calls:
                    tools_used.append(tool_call.name)
                    result = await self.tools.execute(tool_call.name, tool_call.arguments)
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_call.name,
                        "content": result
                    })
            else:
                final_content = response.content
                break
                
        return final_content, tools_used
