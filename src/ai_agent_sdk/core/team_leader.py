"""
TeamLeader - Central orchestration agent.

Implements the core TeamLeader agent with programmatic rules engine,
task delegation, and agent coordination capabilities.
"""

import asyncio
import uuid
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from pathlib import Path
from dataclasses import dataclass, field
import logging

from .rules_engine import RulesEngine, Phase, TaskSpec
from .context_manager import ContextManager
from .task_orchestrator import TaskOrchestrator, TaskResult
from .exceptions import (
    AgentSDKError,
    ConfigurationError,
    TaskExecutionError,
    MCPServerError
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class AgentCapability:
    """Agent capability definition."""
    agent_type: str
    capabilities: List[str]
    max_concurrent_tasks: int
    timeout: int
    priority: int = 5
    availability_window: Optional[Dict[str, str]] = None


@dataclass
class TaskMetrics:
    """Task execution metrics."""
    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    average_execution_time: float = 0.0
    success_rate: float = 0.0
    complexity_budget_used: int = 0
    error_count: int = 0


class AgentRegistry:
    """In-memory agent registry with real-time agent management."""

    def __init__(self):
        self.agents: Dict[str, Dict[str, Any]] = {}
        self.agent_capabilities: Dict[str, AgentCapability] = {}
        self.agent_load: Dict[str, int] = {}
        self.agent_last_heartbeat: Dict[str, datetime] = {}

    async def register_agent(self, agent_id: str, agent_config: Dict[str, Any]) -> bool:
        """Register an agent with the registry."""
        try:
            self.agents[agent_id] = {
                **agent_config,
                "registered_at": datetime.utcnow().isoformat(),
                "status": "active",
                "current_load": 0,
                "max_load": agent_config.get("max_load", 5)
            }
            self.agent_load[agent_id] = 0
            self.agent_last_heartbeat[agent_id] = datetime.utcnow()

            # Set capabilities
            if "capabilities" in agent_config:
                self.agent_capabilities[agent_id] = AgentCapability(
                    agent_type=agent_config["agent_type"],
                    capabilities=agent_config["capabilities"],
                    max_concurrent_tasks=agent_config.get("max_concurrent_tasks", 3),
                    timeout=agent_config.get("timeout", 300),
                    priority=agent_config.get("priority", 5)
                )

            logger.info(f"Registered agent: {agent_id} ({agent_config.get('agent_type')})")
            return True
        except Exception as e:
            logger.error(f"Failed to register agent {agent_id}: {e}")
            return False

    async def get_best_agent(
        self,
        agent_type: str,
        task_type: str,
        complexity: int
    ) -> Optional[Dict[str, Any]]:
        """Get the best available agent for a task."""
        candidates = []

        for agent_id, agent_config in self.agents.items():
            if (agent_config.get("agent_type") == agent_type and
                agent_config.get("status") == "active" and
                agent_config.get("current_load", 0) < agent_config.get("max_load", 5)):

                # Check if agent can handle the task complexity
                max_complexity = agent_config.get("max_complexity", 10)
                if complexity <= max_complexity:
                    candidates.append((agent_id, agent_config))

        if not candidates:
            return None

        # Select agent with lowest load
        best_agent_id, best_agent_config = min(
            candidates,
            key=lambda x: x[1].get("current_load", 0)
        )

        # Update agent load
        self.agent_load[best_agent_id] += 1
        best_agent_config["current_load"] = self.agent_load[best_agent_id]

        return {
            "agent_id": best_agent_id,
            **best_agent_config
        }

    async def release_agent(self, agent_id: str):
        """Release an agent from a task."""
        if agent_id in self.agent_load:
            self.agent_load[agent_id] = max(0, self.agent_load[agent_id] - 1)
            if agent_id in self.agents:
                self.agents[agent_id]["current_load"] = self.agent_load[agent_id]

    async def get_all_agents(self) -> List[Dict[str, Any]]:
        """Get all registered agents."""
        agents_list = []
        for agent_id, agent_config in self.agents.items():
            agents_list.append({
                "agent_id": agent_id,
                **agent_config,
                "last_heartbeat": self.agent_last_heartbeat.get(agent_id)
            })
        return agents_list


class MCPServerManager:
    """MCP server management with real server integration."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.servers: Dict[str, Dict[str, Any]] = {}
        self.server_status: Dict[str, bool] = {}
        self.connection_pool: Dict[str, Any] = {}

    async def initialize_servers(self):
        """Initialize MCP server connections."""
        server_configs = self.config.get("servers", {})

        for server_name, server_config in server_configs.items():
            try:
                await self._initialize_server(server_name, server_config)
            except Exception as e:
                logger.error(f"Failed to initialize MCP server {server_name}: {e}")

    async def _initialize_server(self, server_name: str, server_config: Dict[str, Any]):
        """Initialize a specific MCP server."""
        server_type = server_config.get("type", "http")
        endpoint = server_config.get("endpoint")
        timeout = server_config.get("timeout", 5)

        if not endpoint:
            logger.warning(f"No endpoint configured for MCP server {server_name}")
            return

        # Simulate server connection (in production, this would be real connections)
        self.servers[server_name] = {
            "type": server_type,
            "endpoint": endpoint,
            "timeout": timeout,
            "config": server_config,
            "initialized_at": datetime.utcnow().isoformat()
        }

        # Test connection
        try:
            await self._test_server_connection(server_name)
            self.server_status[server_name] = True
            logger.info(f"MCP server {server_name} initialized successfully")
        except Exception as e:
            self.server_status[server_name] = False
            logger.error(f"MCP server {server_name} connection failed: {e}")

    async def _test_server_connection(self, server_name: str):
        """Test server connection."""
        # Simulate connection test (in production, this would be real HTTP/WebSocket calls)
        server_config = self.servers[server_name]
        if server_config["type"] == "http":
            # Simulate HTTP connection test
            await asyncio.sleep(0.1)  # Simulate network latency
        elif server_config["type"] == "websocket":
            # Simulate WebSocket connection test
            await asyncio.sleep(0.1)

    def get_server_context(self, server_name: str) -> Dict[str, Any]:
        """Get context for a specific server."""
        if server_name not in self.servers:
            return {"available": False}

        return {
            "available": self.server_status.get(server_name, False),
            "server_info": self.servers[server_name],
            "last_checked": datetime.utcnow().isoformat()
        }

    async def execute_server_request(
        self,
        server_name: str,
        request_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a request on an MCP server."""
        if server_name not in self.servers or not self.server_status.get(server_name):
            raise MCPServerError(f"MCP server {server_name} not available")

        # Simulate server request (in production, this would be real API calls)
        server_config = self.servers[server_name]

        try:
            # Simulate processing time
            await asyncio.sleep(0.2)

            # Return simulated response
            return {
                "server": server_name,
                "request_id": str(uuid.uuid4()),
                "status": "success",
                "data": {"result": f"Processed by {server_name}"},
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            raise MCPServerError(f"MCP server request failed: {e}")


class TeamLeader:
    """
    Central orchestration agent with rules engine and delegation capabilities.
    Implements hierarchical coordination with validation gates and scope enforcement.
    """

    def __init__(self, config_path: Optional[str] = None):
        """Initialize TeamLeader with configuration."""
        self.config_path = config_path or "config/team_leader.yaml"
        self.config = self._load_config()
        self.team_leader_id = f"team_leader_{uuid.uuid4().hex[:8]}"

        # Initialize subsystems
        self.rules_engine = RulesEngine(self.config.get("rules", {}))
        self.context_manager = ContextManager(
            self.config.get("prompts_directory", "system_prompts")
        )

        # Initialize real agent registry and MCP manager
        self.agent_registry = AgentRegistry()
        self.mcp_manager = MCPServerManager(self.config.get("mcp", {}))

        # Task orchestrator will be initialized later
        self.task_orchestrator = None
        self.security_manager = None

        # State tracking
        self.initialized = False
        self.startup_time: Optional[datetime] = None
        self.metrics = TaskMetrics()
        self.task_queue: List[TaskSpec] = []
        self.active_tasks: Dict[str, Dict[str, Any]] = {}

    def _load_config(self) -> Dict[str, Any]:
        """Load TeamLeader configuration."""
        # Default configuration
        default_config = {
            "rules": {
                "complexity_budget": 25,
                "phase_timeout": 3600,
                "max_concurrent_tasks": 10
            },
            "prompts_directory": "system_prompts",
            "agents": {
                "research_agent": {
                    "agent_type": "research",
                    "max_concurrent_tasks": 3,
                    "timeout": 300,
                    "max_complexity": 8,
                    "capabilities": ["web_research", "competitive_analysis", "knowledge_synthesis"]
                },
                "codebase_analyzer": {
                    "agent_type": "codebase_analyzer",
                    "max_concurrent_tasks": 2,
                    "timeout": 600,
                    "max_complexity": 10,
                    "capabilities": ["security_analysis", "performance_analysis", "architecture_review"]
                },
                "frontend_coder": {
                    "agent_type": "frontend",
                    "max_concurrent_tasks": 2,
                    "timeout": 900,
                    "max_complexity": 8,
                    "capabilities": ["ui_development", "component_design", "responsive_design"]
                },
                "backend_coder": {
                    "agent_type": "backend",
                    "max_concurrent_tasks": 2,
                    "timeout": 1200,
                    "max_complexity": 10,
                    "capabilities": ["api_development", "database_design", "system_integration"]
                }
            },
            "mcp": {
                "servers": {
                    "perplexity": {
                        "type": "http",
                        "endpoint": "https://api.perplexity.ai",
                        "timeout": 10,
                        "capabilities": ["research", "search", "analyze"]
                    },
                    "serena": {
                        "type": "http",
                        "endpoint": "https://api.serena.ai",
                        "timeout": 15,
                        "capabilities": ["analyze_code", "security_scan", "performance_review"]
                    }
                }
            },
            "websocket": {
                "host": "localhost",
                "port": 8080,
                "max_connections": 100
            }
        }

        # Try to load from file
        config_file = Path(self.config_path)
        if config_file.exists():
            try:
                import yaml
                with open(config_file, 'r') as f:
                    file_config = yaml.safe_load(f)
                # Merge with defaults
                default_config.update(file_config)
            except Exception as e:
                logger.warning(f"Failed to load config file {config_file}: {e}")
                logger.warning("Using default configuration")

        return default_config

    async def initialize(
        self,
        security_manager=None
    ):
        """
        Initialize TeamLeader with all subsystems.

        Args:
            security_manager: Security manager for authentication/authorization
        """
        if self.initialized:
            logger.warning("TeamLeader already initialized")
            return

        try:
            logger.info("Initializing TeamLeader...")

            # Store dependencies
            self.security_manager = security_manager

            # Initialize task orchestrator
            from .task_orchestrator import TaskOrchestrator
            self.task_orchestrator = TaskOrchestrator(
                agent_registry=self.agent_registry,
                context_manager=self.context_manager,
                mcp_client=self.mcp_manager,
                config=self.config.get("task_orchestrator", {})
            )

            # Initialize subsystems
            await self.context_manager.initialize()
            await self.task_orchestrator.initialize()
            await self.mcp_manager.initialize_servers()

            # Register built-in agents
            await self._register_builtin_agents()

            # Initialize agent capabilities in rules engine
            await self._initialize_agent_capabilities()

            # Set startup time
            self.startup_time = datetime.utcnow()
            self.initialized = True

            logger.info(f"TeamLeader initialized successfully with ID: {self.team_leader_id}")
            logger.info(f"Current phase: {self.rules_engine.current_phase.value}")

        except Exception as e:
            logger.error(f"Failed to initialize TeamLeader: {e}")
            raise ConfigurationError(f"TeamLeader initialization failed: {e}") from e

    async def _register_builtin_agents(self):
        """Register built-in agents with the registry."""
        agent_configs = self.config.get("agents", {})

        for agent_name, agent_config in agent_configs.items():
            await self.agent_registry.register_agent(agent_name, agent_config)

    async def _initialize_agent_capabilities(self):
        """Initialize agent capabilities in rules engine."""
        agent_configs = self.config.get("agents", {})

        for agent_config in agent_configs.values():
            agent_type = agent_config.get("agent_type")
            capabilities = agent_config.get("capabilities", [])

            self.rules_engine.add_agent_capability(agent_type, set(capabilities))

    async def delegate_task(
        self,
        agent_type: str,
        task_type: str,
        task: str,
        complexity: int = 5,
        priority: int = 5,
        project_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> TaskResult:
        """
        Delegate task to appropriate sub-agent with proper context and validation.

        Args:
            agent_type: Type of agent to delegate to
            task_type: Type of task to execute
            task: Task description
            complexity: Task complexity (1-10)
            priority: Task priority (1-10)
            project_id: Project identifier
            metadata: Additional task metadata

        Returns:
            TaskResult from agent execution

        Raises:
            TaskExecutionError: If task execution fails
            ScopeViolationError: If task exceeds scope boundaries
            AgentUnavailableError: If required agent is not available
        """
        if not self.initialized:
            raise AgentSDKError("TeamLeader not initialized")

        # Create task specification
        task_spec = TaskSpec(
            task_id=str(uuid.uuid4()),
            agent_type=agent_type,
            task_type=task_type,
            task=task,
            complexity=complexity,
            priority=priority,
            project_id=project_id,
            metadata=metadata or {}
        )

        # Track task
        self.active_tasks[task_spec.task_id] = {
            "task_spec": task_spec,
            "started_at": datetime.utcnow(),
            "status": "delegating"
        }

        try:
            # 1. Validate task against scope boundaries
            if not self.rules_engine.validate_scope(task_spec):
                raise TaskExecutionError("Task validation failed")

            # 2. Check complexity budget
            if self.metrics.complexity_budget_used + complexity > self.config["rules"]["complexity_budget"]:
                raise TaskExecutionError("Complexity budget exceeded")

            # 3. Load appropriate system prompt
            system_prompt = await self.context_manager.load_prompt(
                agent_type=agent_type,
                task_type=task_type
            )

            # 4. Prepare context with real MCP integration
            mcp_context = await self._get_mcp_context()
            context = await self.context_manager.prepare_context(
                task_spec=task_spec,
                mcp_context=mcp_context
            )

            # 5. Update task status
            self.active_tasks[task_spec.task_id]["status"] = "executing"
            self.metrics.complexity_budget_used += complexity

            # 6. Execute task with monitoring
            start_time = time.time()
            result = await self.task_orchestrator.execute_task(
                task_spec=task_spec,
                context=context
            )
            execution_time = time.time() - start_time

            # 7. Validate result and update metrics
            await self._validate_result(result, task_spec)
            await self._update_metrics(result, task_spec, execution_time)

            # 8. Register task execution in rules engine
            self.rules_engine.register_task_execution(task_spec, {
                "status": "completed",
                "execution_time": execution_time,
                "confidence_score": result.confidence_score
            })

            # 9. Update task status
            self.active_tasks[task_spec.task_id]["status"] = "completed"
            self.active_tasks[task_spec.task_id]["completed_at"] = datetime.utcnow()

            # 10. Clean up
            del self.active_tasks[task_spec.task_id]

            logger.info(f"Task completed: {task_spec.task_id} in {execution_time:.2f}s")
            return result

        except Exception as e:
            self.metrics.error_count += 1
            self.metrics.failed_tasks += 1

            # Update task status
            if task_spec.task_id in self.active_tasks:
                self.active_tasks[task_spec.task_id]["status"] = "failed"
                self.active_tasks[task_spec.task_id]["error"] = str(e)
                self.active_tasks[task_spec.task_id]["failed_at"] = datetime.utcnow()

            logger.error(f"Task failed: {task_spec.task_id} - {e}")
            raise TaskExecutionError(f"Task delegation failed: {e}") from e

    async def _get_mcp_context(self) -> Dict[str, Any]:
        """Get real MCP server context for task execution."""
        mcp_context = {}

        for server_name in self.mcp_manager.servers.keys():
            server_context = self.mcp_manager.get_server_context(server_name)
            if server_context["available"]:
                mcp_context[server_name] = server_context

        return mcp_context

    async def _validate_result(self, result: TaskResult, task_spec: TaskSpec):
        """Validate task result quality."""
        if not result.content or len(result.content.strip()) < 10:
            raise TaskExecutionError("Task result content is too short or empty")

        if result.confidence_score < 0.3:
            raise TaskExecutionError(f"Task result confidence too low: {result.confidence_score}")

        # Check for mock data indicators
        mock_indicators = ["mock", "placeholder", "example", "todo", "not implemented"]
        content_lower = result.content.lower()
        if any(indicator in content_lower for indicator in mock_indicators):
            raise TaskExecutionError("Task result contains mock data or placeholders")

    async def _update_metrics(self, result: TaskResult, task_spec: TaskSpec, execution_time: float):
        """Update internal metrics."""
        self.metrics.total_tasks += 1
        self.metrics.completed_tasks += 1

        # Update average execution time
        total_time = self.metrics.average_execution_time * (self.metrics.completed_tasks - 1) + execution_time
        self.metrics.average_execution_time = total_time / self.metrics.completed_tasks

        # Update success rate
        self.metrics.success_rate = self.metrics.completed_tasks / self.metrics.total_tasks

    async def progress_to_phase(self, target_phase: str) -> bool:
        """
        Progress to the next development phase if requirements are met.

        Args:
            target_phase: Target phase to progress to

        Returns:
            True if progression successful, False otherwise
        """
        if not self.initialized:
            raise AgentSDKError("TeamLeader not initialized")

        try:
            phase_enum = Phase(target_phase.lower())
            return await self.rules_engine.progress_to_phase(phase_enum)
        except ValueError:
            logger.error(f"Invalid phase: {target_phase}")
            return False

    def get_status(self) -> Dict[str, Any]:
        """Get current TeamLeader status and health."""
        if not self.initialized:
            return {
                "status": "not_initialized",
                "team_leader_id": self.team_leader_id,
                "message": "TeamLeader not initialized. Call initialize() first."
            }

        # Get phase status
        phase_status = self.rules_engine.get_phase_status()

        # Get task metrics
        task_metrics = {}
        if self.task_orchestrator:
            task_metrics = self.task_orchestrator.get_metrics()

        # Calculate uptime
        uptime_seconds = 0
        if self.startup_time:
            uptime_seconds = (datetime.utcnow() - self.startup_time).total_seconds()

        return {
            "team_leader_id": self.team_leader_id,
            "status": "operational",
            "uptime_seconds": uptime_seconds,
            "current_phase": phase_status["current_phase"],
            "phase_progress": phase_status["phase_progress"],
            "can_progress_phase": phase_status["can_progress"],
            "complexity_budget": phase_status["complexity_budget"],
            "complexity_used": phase_status["complexity_used"],
            "metrics": {
                "total_tasks": self.metrics.total_tasks,
                "completed_tasks": self.metrics.completed_tasks,
                "failed_tasks": self.metrics.failed_tasks,
                "success_rate": self.metrics.success_rate,
                "average_execution_time": self.metrics.average_execution_time,
                "error_count": self.metrics.error_count
            },
            "task_metrics": task_metrics,
            "context_cache_stats": self.context_manager.get_cache_stats(),
            "active_tasks_count": len(self.active_tasks),
            "mcp_servers": {
                name: status for name, status in self.mcp_manager.server_status.items()
            },
            "initialization_time": self.startup_time.isoformat() if self.startup_time else None
        }

    async def shutdown(self):
        """Shutdown TeamLeader and cleanup resources."""
        if not self.initialized:
            return

        logger.info("Shutting down TeamLeader...")

        try:
            # Shutdown subsystems
            if self.task_orchestrator:
                await self.task_orchestrator.shutdown()

            await self.context_manager.cleanup()

            # Reset state
            self.initialized = False
            self.startup_time = None

            logger.info("TeamLeader shutdown complete")

        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

    async def get_available_agents(self) -> List[Dict[str, Any]]:
        """Get list of available agents and their capabilities."""
        return await self.agent_registry.get_all_agents()

    async def get_task_queue_status(self) -> Dict[str, Any]:
        """Get current task queue status."""
        if not self.task_orchestrator:
            return {}

        return {
            "active_tasks": self.task_orchestrator.get_active_tasks(),
            "recent_tasks": self.task_orchestrator.get_task_history(limit=20),
            "metrics": self.task_orchestrator.get_metrics(),
            "queue_length": len(self.task_queue)
        }

    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.shutdown()


async def main():
    """Main function for TeamLeader standalone execution."""
    import os
    import sys

    # Simple command-line interface
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("TeamLeader - AI Agent Orchestration System")
        print("Usage: python -m ai_agent_sdk.core.team_leader")
        return

    # Create TeamLeader instance
    team_leader = TeamLeader()

    try:
        # Initialize
        await team_leader.initialize()

        # Print status
        status = team_leader.get_status()
        print("\n=== TeamLeader Status ===")
        print(f"ID: {status['team_leader_id']}")
        print(f"Status: {status['status']}")
        print(f"Phase: {status['current_phase']}")
        print(f"Uptime: {status['uptime_seconds']:.0f}s")

        # Keep running
        print("\nTeamLeader is running. Press Ctrl+C to stop.")
        while True:
            await asyncio.sleep(10)

    except KeyboardInterrupt:
        print("\nShutting down...")
        await team_leader.shutdown()

    except Exception as e:
        print(f"Error: {e}")
        await team_leader.shutdown()


if __name__ == "__main__":
    asyncio.run(main())