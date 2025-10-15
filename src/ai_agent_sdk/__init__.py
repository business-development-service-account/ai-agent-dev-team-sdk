"""
AI Agent Dev Team SDK - Core Foundation Infrastructure

A comprehensive SDK for building AI agent development teams with hierarchical coordination,
real-time communication, and enterprise-grade security.
"""

__version__ = "1.0.0"
__author__ = "AI Agent SDK Team"
__email__ = "team@ai-agent-sdk.com"

from .core.team_leader import TeamLeader
from .agents.base_agent import BaseAgent
from .communication.websocket_server import AgentCommunicationHub
from .security.auth_manager import SecurityManager
from .database.models import Agent, Task, TaskResult

__all__ = [
    "TeamLeader",
    "BaseAgent",
    "AgentCommunicationHub",
    "SecurityManager",
    "Agent",
    "Task",
    "TaskResult",
]