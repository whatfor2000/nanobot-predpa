"""Message tool for sending messages to users."""

from typing import Any, Callable, Awaitable

from nanobot.agent.tools.base import Tool
from nanobot.bus.events import OutboundMessage, InboundMessage
import nanobot.bus.queue

class MessageTool(Tool):
    """Tool to send messages to users on chat channels."""
    
    def __init__(
        self, 
        send_callback: Callable[[OutboundMessage], Awaitable[None]] | None = None,
        default_channel: str = "",
        default_chat_id: str = ""
    ):
        self._send_callback = send_callback
        self._default_channel = default_channel
        self._default_chat_id = default_chat_id
    
    def set_context(self, channel: str, chat_id: str) -> None:
        """Set the current message context."""
        self._default_channel = channel
        self._default_chat_id = chat_id
    
    def set_send_callback(self, callback: Callable[[OutboundMessage], Awaitable[None]]) -> None:
        """Set the callback for sending messages."""
        self._send_callback = callback
    
    @property
    def name(self) -> str:
        return "message"
    
    @property
    def description(self) -> str:
        return "Send a message to the user/channel. Use this when you want to communicate something."
    
    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "content": {
                    "type": "string",
                    "description": "The message content to send"
                },
                "channel": {
                    "type": "string",
                    "description": "Optional: target channel (telegram, discord, etc.)"
                },
                "chat_id": {
                    "type": "string",
                    "description": "Optional: target chat/user ID"
                }
            },
            "required": ["content"]
        }
    
    async def execute(
        self, 
        content: str, 
        channel: str | None = None, 
        chat_id: str | None = None,
        **kwargs: Any
    ) -> str:
        channel = channel or self._default_channel
        chat_id = chat_id or self._default_chat_id
        
        if not channel or not chat_id:
            return "Error: No target channel/chat specified"
        
        if not self._send_callback:
            return "Error: Message sending not configured"
        
        msg = OutboundMessage(
            channel=channel,
            chat_id=chat_id,
            content=content
        )
        
        try:
            await self._send_callback(msg)
            return f"Message sent to {channel}:{chat_id}"
        except Exception as e:
            return f"Error sending message: {str(e)}"

class SendMessageTool(Tool):
    """Tool for sending messages to other agents."""
    
    name = "send_message"
    description = "Send a message to another agent or the manager."
    parameters = {
        "type": "object",
        "properties": {
            "recipient_role": {
                "type": "string",
                "description": "The role of the recipient agent (e.g., 'researcher', 'coder', 'manager')."
            },
            "content": {
                "type": "string",
                "description": "The content of the message."
            }
        },
        "required": ["recipient_role", "content"]
    }

    def __init__(self, bus: "nanobot.bus.queue.MessageBus", sender_role: str):
        self.bus = bus
        self.sender_role = sender_role

    async def execute(self, recipient_role: str, content: str) -> str:
        """Send a message to another agent."""
        msg = InboundMessage(
            channel=f"agent:{recipient_role}",
            sender_id=f"agent:{self.sender_role}",
            chat_id="direct", # Internal communication
            content=content
        )
        await self.bus.publish_inbound(msg)
        return f"Message sent to agent:{recipient_role}"
