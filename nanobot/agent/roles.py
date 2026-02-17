from enum import Enum

class AgentRole(str, Enum):
    """Standard agent roles."""
    MANAGER = "manager"
    RESEARCHER = "researcher"
    CODER = "coder"
    CRITIC = "critic"
