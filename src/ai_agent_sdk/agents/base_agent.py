"""
Base Agent class for AI Agent SDK.

Provides the foundation for all specialized agents with Claude SDK integration,
common functionality, and standardized interfaces.
"""

import asyncio
import time
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    Anthropic = None

from ..core.exceptions import (
    AgentSDKError,
    TaskExecutionError,
    MCPServerError,
    ConfigurationError
)
from ..core.rules_engine import TaskSpec
from ..core.context_manager import AgentContext
from ..core.task_orchestrator import TaskResult


class AgentStatus(Enum):
    """Agent operational status."""
    OFFLINE = "offline"
    STARTING = "starting"
    ONLINE = "online"
    BUSY = "busy"
    MAINTENANCE = "maintenance"
    ERROR = "error"


@dataclass
class AgentCapability:
    """Agent capability definition."""
    name: str
    description: str
    requires_mcp: bool = False
    mcp_server: Optional[str] = None
    supported_task_types: Set[str] = field(default_factory=set)


@dataclass
class AgentMetrics:
    """Agent performance metrics."""
    total_tasks: int = 0
    successful_tasks: int = 0
    failed_tasks: int = 0
    average_execution_time: float = 0.0
    current_load: float = 0.0
    last_heartbeat: Optional[datetime] = None
    uptime_seconds: float = 0.0


class BaseAgent(ABC):
    """
    Base class for all specialized sub-agents with Claude SDK integration.
    Provides common functionality for task execution and communication.
    """

    def __init__(
        self,
        agent_type: str,
        agent_id: Optional[str] = None,
        config: Dict[str, Any] = None
    ):
        """Initialize base agent."""
        self.agent_id = agent_id or f"{agent_type}_{uuid.uuid4().hex[:8]}"
        self.agent_type = agent_type
        self.config = config or {}
        self.status = AgentStatus.OFFLINE
        self.capabilities: List[AgentCapability] = []
        self.supported_task_types: Set[str] = set()
        self.mcp_integrations: Dict[str, Any] = {}

        # Claude SDK client
        self.claude_client: Optional[Anthropic] = None
        self.claude_model = self.config.get("claude_model", "claude-3-sonnet-20241022")
        self.max_tokens = self.config.get("max_tokens", 4096)
        self.temperature = self.config.get("temperature", 0.3)

        # Metrics and state
        self.metrics = AgentMetrics()
        self.startup_time: Optional[datetime] = None
        self.current_tasks: Set[str] = set()
        self.max_concurrent_tasks = self.config.get("max_concurrent_tasks", 3)

        # MCP client (injected)
        self.mcp_client = None

        # Security context
        self.security_context: Dict[str, Any] = {}

    async def initialize(
        self,
        mcp_client=None,
        security_context: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize agent with external dependencies.

        Args:
            mcp_client: MCP client for external service integration
            security_context: Security context and permissions
        """
        if self.status != AgentStatus.OFFLINE:
            return

        try:
            self.status = AgentStatus.STARTING

            # Initialize Claude client
            await self._initialize_claude_client()

            # Setup MCP integrations
            if mcp_client:
                self.mcp_client = mcp_client
                await self._setup_mcp_integrations()

            # Set security context
            if security_context:
                self.security_context = security_context

            # Initialize capabilities
            await self._initialize_capabilities()

            # Set startup time and status
            self.startup_time = datetime.utcnow()
            self.status = AgentStatus.ONLINE

            print(f"Agent {self.agent_id} ({self.agent_type}) initialized successfully")

        except Exception as e:
            self.status = AgentStatus.ERROR
            raise ConfigurationError(f"Failed to initialize agent {self.agent_id}: {e}") from e

    async def _initialize_claude_client(self):
        """Initialize Claude SDK client."""
        api_key = self.config.get("anthropic_api_key")
        if not api_key:
            api_key = self._get_anthropic_api_key()

        if not api_key:
            raise ConfigurationError("Anthropic API key not provided")

        self.claude_client = Anthropic(api_key=api_key)

    def _get_anthropic_api_key(self) -> Optional[str]:
        """Get Anthropic API key from environment or config."""
        import os
        return os.getenv("ANTHROPIC_API_KEY")

    async def _setup_mcp_integrations(self):
        """Setup MCP server integrations."""
        if not self.mcp_client:
            return

        # Setup integrations based on agent capabilities
        for capability in self.capabilities:
            if capability.requires_mcp and capability.mcp_server:
                try:
                    # In a real implementation, this would setup specific MCP integrations
                    self.mcp_integrations[capability.mcp_server] = {
                        "available": True,
                        "setup_time": datetime.utcnow().isoformat()
                    }
                except Exception as e:
                    print(f"Warning: Failed to setup MCP integration for {capability.mcp_server}: {e}")

    @abstractmethod
    async def _initialize_capabilities(self):
        """Initialize agent-specific capabilities."""
        pass

    async def execute_task(
        self,
        task_spec: TaskSpec,
        context: Optional[AgentContext] = None
    ) -> TaskResult:
        """
        Execute task using Claude SDK with comprehensive error handling and monitoring.

        Args:
            task_spec: Task specification
            context: Agent context for execution

        Returns:
            TaskResult with execution results

        Raises:
            TaskExecutionError: If task execution fails
        """
        if self.status != AgentStatus.ONLINE:
            raise TaskExecutionError(f"Agent {self.agent_id} is not online (status: {self.status.value})")

        # Check concurrent task limit
        if len(self.current_tasks) >= self.max_concurrent_tasks:
            raise TaskExecutionError(f"Agent {self.agent_id} has reached maximum concurrent tasks")

        task_start_time = time.time()
        task_id = task_spec.task_id

        try:
            # Add to current tasks
            self.current_tasks.add(task_id)

            # Update metrics
            self.metrics.current_load = len(self.current_tasks) / self.max_concurrent_tasks
            self.metrics.last_heartbeat = datetime.utcnow()

            print(f"Starting task {task_id} on agent {self.agent_id}")

            # Prepare for execution
            await self._prepare_task_execution(task_spec, context)

            # Execute task
            result = await self._execute_task_internal(task_spec, context)

            # Update metrics on success
            execution_time = time.time() - task_start_time
            self.metrics.total_tasks += 1
            self.metrics.successful_tasks += 1
            self._update_average_execution_time(execution_time)

            print(f"Completed task {task_id} on agent {self.agent_id} in {execution_time:.2f}s")

            return result

        except Exception as e:
            # Update metrics on failure
            self.metrics.total_tasks += 1
            self.metrics.failed_tasks += 1

            execution_time = time.time() - task_start_time
            print(f"Failed task {task_id} on agent {self.agent_id} after {execution_time:.2f}s: {e}")

            # Convert to TaskExecutionError if needed
            if not isinstance(e, TaskExecutionError):
                raise TaskExecutionError(f"Task execution failed: {e}") from e

            raise

        finally:
            # Remove from current tasks
            self.current_tasks.discard(task_id)
            self.metrics.current_load = len(self.current_tasks) / self.max_concurrent_tasks

    async def _prepare_task_execution(
        self,
        task_spec: TaskSpec,
        context: Optional[AgentContext]
    ):
        """Prepare for task execution."""
        # Validate task is supported
        if task_spec.task_type not in self.supported_task_types:
            raise TaskExecutionError(
                f"Task type {task_spec.task_type} not supported by agent {self.agent_id}"
            )

        # Validate security context
        await self._validate_security_context(task_spec)

    async def _validate_security_context(self, task_spec: TaskSpec):
        """Validate task against security context."""
        # Check if agent has required permissions
        if not self.security_context:
            return

        permissions = self.security_context.get("permissions", [])
        required_permission = f"task:{task_spec.task_type}"

        if required_permission not in permissions:
            raise TaskExecutionError(
                f"Agent {self.agent_id} lacks permission for task type {task_spec.task_type}"
            )

    @abstractmethod
    async def _execute_task_internal(
        self,
        task_spec: TaskSpec,
        context: Optional[AgentContext]
    ) -> TaskResult:
        """Execute the internal task logic."""
        pass

    async def _call_claude(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Call Claude API with message processing.

        Args:
            messages: List of messages for Claude
            system_prompt: Optional system prompt

        Returns:
            Claude response content

        Raises:
            TaskExecutionError: If Claude call fails
        """
        if not self.claude_client:
            raise TaskExecutionError("Claude client not initialized")

        try:
            response = await asyncio.to_thread(
                self.claude_client.messages.create,
                model=self.claude_model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=system_prompt,
                messages=messages
            )

            return response.content[0].text if response.content else ""

        except Exception as e:
            raise TaskExecutionError(f"Claude API call failed: {e}") from e

    async def _call_mcp_server(
        self,
        server_name: str,
        method: str,
        params: Dict[str, Any]
    ) -> Any:
        """
        Call MCP server method.

        Args:
            server_name: Name of MCP server
            method: Method to call
            params: Parameters for method

        Returns:
            MCP server response

        Raises:
            MCPServerError: If MCP call fails
        """
        if not self.mcp_client:
            raise MCPServerError("MCP client not available")

        if server_name not in self.mcp_integrations:
            raise MCPServerError(f"MCP server {server_name} not integrated")

        try:
            # In a real implementation, this would call the actual MCP server
            return await self.mcp_client.call(server_name, method, params)

        except Exception as e:
            raise MCPServerError(f"MCP server call failed: {e}") from e

    def _update_average_execution_time(self, execution_time: float):
        """Update average execution time metric."""
        if self.metrics.total_tasks == 1:
            self.metrics.average_execution_time = execution_time
        else:
            # Running average
            self.metrics.average_execution_time = (
                (self.metrics.average_execution_time * (self.metrics.total_tasks - 1) + execution_time) /
                self.metrics.total_tasks
            )

    def _create_task_result(
        self,
        task_id: str,
        content: str,
        confidence_score: float = 0.8,
        sources: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> TaskResult:
        """Create a standardized task result."""
        return TaskResult(
            task_id=task_id,
            agent_id=self.agent_id,
            status="completed",  # Will be updated by orchestrator if needed
            content=content,
            execution_time=0.0,  # Will be set by orchestrator
            confidence_score=confidence_score,
            sources=sources or [],
            metadata=metadata or {}
        )

    async def send_heartbeat(self):
        """Send heartbeat to indicate agent is alive."""
        self.metrics.last_heartbeat = datetime.utcnow()
        if self.startup_time:
            self.metrics.uptime_seconds = (
                datetime.utcnow() - self.startup_time
            ).total_seconds()

    def get_status(self) -> Dict[str, Any]:
        """Get current agent status and metrics."""
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "status": self.status.value,
            "capabilities": [
                {
                    "name": cap.name,
                    "description": cap.description,
                    "requires_mcp": cap.requires_mcp,
                    "mcp_server": cap.mcp_server
                }
                for cap in self.capabilities
            ],
            "supported_task_types": list(self.supported_task_types),
            "current_tasks": len(self.current_tasks),
            "max_concurrent_tasks": self.max_concurrent_tasks,
            "metrics": {
                "total_tasks": self.metrics.total_tasks,
                "successful_tasks": self.metrics.successful_tasks,
                "failed_tasks": self.metrics.failed_tasks,
                "success_rate": (
                    self.metrics.successful_tasks / self.metrics.total_tasks
                    if self.metrics.total_tasks > 0 else 0
                ),
                "average_execution_time": self.metrics.average_execution_time,
                "current_load": self.metrics.current_load,
                "uptime_seconds": self.metrics.uptime_seconds
            },
            "last_heartbeat": (
                self.metrics.last_heartbeat.isoformat()
                if self.metrics.last_heartbeat else None
            ),
            "mcp_integrations": list(self.mcp_integrations.keys()),
            "claude_model": self.claude_model
        }

    async def shutdown(self):
        """Shutdown agent and cleanup resources."""
        if self.status == AgentStatus.OFFLINE:
            return

        print(f"Shutting down agent {self.agent_id}...")

        # Wait for current tasks to complete or timeout
        if self.current_tasks:
            print(f"Waiting for {len(self.current_tasks)} tasks to complete...")
            timeout = 30  # 30 seconds
            start_time = time.time()

            while self.current_tasks and (time.time() - start_time) < timeout:
                await asyncio.sleep(1)

        # Set status to offline
        self.status = AgentStatus.OFFLINE

        print(f"Agent {self.agent_id} shutdown complete")

    def _add_capability(
        self,
        name: str,
        description: str,
        requires_mcp: bool = False,
        mcp_server: Optional[str] = None,
        supported_task_types: Optional[Set[str]] = None
    ):
        """Add a capability to the agent."""
        capability = AgentCapability(
            name=name,
            description=description,
            requires_mcp=requires_mcp,
            mcp_server=mcp_server,
            supported_task_types=supported_task_types or set()
        )
        self.capabilities.append(capability)

        # Update supported task types
        if supported_task_types:
            self.supported_task_types.update(supported_task_types)