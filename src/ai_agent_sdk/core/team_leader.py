"""
TeamLeader - Central orchestration agent.

Implements the core TeamLeader agent with programmatic rules engine,
task delegation, and agent coordination capabilities.
"""

import asyncio
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

from .rules_engine import RulesEngine, Phase, TaskSpec
from .context_manager import ContextManager
from .task_orchestrator import TaskOrchestrator, TaskResult
from .exceptions import (
    AgentSDKError,
    ConfigurationError,
    TaskExecutionError,
    MCPServerError
)


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
        self.task_orchestrator = None  # Will be initialized later
        self.agent_registry = None  # Will be injected
        self.mcp_client = None  # Will be injected
        self.security_manager = None  # Will be injected

        # State tracking
        self.initialized = False
        self.startup_time: Optional[datetime] = None
        self.task_count = 0
        self.error_count = 0

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
            "agent_registry": {
                "research": {
                    "max_concurrent_tasks": 3,
                    "timeout": 300
                },
                "codebase_analyzer": {
                    "max_concurrent_tasks": 2,
                    "timeout": 600
                },
                "frontend": {
                    "max_concurrent_tasks": 2,
                    "timeout": 900
                },
                "backend": {
                    "max_concurrent_tasks": 2,
                    "timeout": 1200
                }
            },
            "websocket": {
                "host": "localhost",
                "port": 8080,
                "max_connections": 100
            },
            "mcp": {
                "timeout": 5,
                "retry_attempts": 3
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
                print(f"Warning: Failed to load config file {config_file}: {e}")
                print("Using default configuration")

        return default_config

    async def initialize(
        self,
        agent_registry=None,
        mcp_client=None,
        security_manager=None
    ):
        """
        Initialize TeamLeader with all subsystems.

        Args:
            agent_registry: Agent registry for task delegation
            mcp_client: MCP client for external service integration
            security_manager: Security manager for authentication/authorization
        """
        if self.initialized:
            print("TeamLeader already initialized")
            return

        try:
            print("Initializing TeamLeader...")

            # Store dependencies
            self.agent_registry = agent_registry
            self.mcp_client = mcp_client
            self.security_manager = security_manager

            # Initialize task orchestrator
            from .task_orchestrator import TaskOrchestrator
            self.task_orchestrator = TaskOrchestrator(
                agent_registry=agent_registry,
                context_manager=self.context_manager,
                mcp_client=mcp_client,
                config=self.config.get("task_orchestrator", {})
            )

            # Initialize subsystems
            await self.context_manager.initialize()
            await self.task_orchestrator.initialize()

            # Initialize MCP connections if available
            if self.mcp_client:
                await self._initialize_mcp_connections()

            # Initialize agent capabilities
            await self._initialize_agent_capabilities()

            # Set startup time
            self.startup_time = datetime.utcnow()
            self.initialized = True

            print(f"TeamLeader initialized successfully with ID: {self.team_leader_id}")
            print(f"Current phase: {self.rules_engine.current_phase.value}")

        except Exception as e:
            print(f"Failed to initialize TeamLeader: {e}")
            raise ConfigurationError(f"TeamLeader initialization failed: {e}") from e

    async def _initialize_mcp_connections(self):
        """Initialize MCP server connections."""
        try:
            if hasattr(self.mcp_client, 'initialize_servers'):
                await self.mcp_client.initialize_servers()
                print("MCP connections initialized")
        except Exception as e:
            print(f"Warning: Failed to initialize MCP connections: {e}")

    async def _initialize_agent_capabilities(self):
        """Initialize agent capabilities in rules engine."""
        if self.agent_registry:
            # Add agent capabilities to rules engine
            agent_types = ["research", "codebase_analyzer", "frontend", "backend"]
            for agent_type in agent_types:
                capabilities = {
                    "research": {"web_research", "competitive_analysis", "knowledge_synthesis"},
                    "codebase_analyzer": {"security_analysis", "performance_analysis", "architecture_review"},
                    "frontend": {"ui_development", "component_design", "responsive_design"},
                    "backend": {"api_development", "database_design", "system_integration"}
                }.get(agent_type, set())

                self.rules_engine.add_agent_capability(agent_type, capabilities)

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

        try:
            # 1. Validate task against scope boundaries
            if not self.rules_engine.validate_scope(task_spec):
                raise TaskExecutionError("Task validation failed")

            # 2. Load appropriate system prompt
            system_prompt = await self.context_manager.load_prompt(
                agent_type=agent_type,
                task_type=task_type
            )

            # 3. Prepare context
            context = await self.context_manager.prepare_context(
                task_spec=task_spec,
                mcp_context=await self._get_mcp_context()
            )

            # 4. Execute task with monitoring
            async with self.task_orchestrator.task_monitor(task_spec) as monitor:
                await monitor.log_event("task_delegated", {
                    "agent_type": agent_type,
                    "task_type": task_type,
                    "complexity": complexity
                })

                result = await self.task_orchestrator.execute_task(
                    task_spec=task_spec,
                    context=context
                )

            # 5. Validate result and update context
            await self._validate_result(result, task_spec)
            await self._update_metrics(result, task_spec)

            # 6. Register task execution in rules engine
            self.rules_engine.register_task_execution(task_spec, {
                "status": "completed",
                "execution_time": result.execution_time,
                "confidence_score": result.confidence_score
            })

            self.task_count += 1

            print(f"Task completed: {task_spec.task_id} in {result.execution_time:.2f}s")
            return result

        except Exception as e:
            self.error_count += 1
            print(f"Task failed: {task_spec.task_id} - {e}")
            raise TaskExecutionError(f"Task delegation failed: {e}") from e

    async def _get_mcp_context(self) -> Dict[str, Any]:
        """Get MCP server context for task execution."""
        if not self.mcp_client:
            return {}

        try:
            # Check MCP server status
            mcp_context = {}

            # Add Perplexity context if available
            if hasattr(self.mcp_client, 'servers') and 'perplexity' in self.mcp_client.servers:
                mcp_context["perplexity"] = {
                    "available": True,
                    "capabilities": ["research", "search", "analyze"]
                }

            # Add Serena context if available
            if hasattr(self.mcp_client, 'servers') and 'serena' in self.mcp_client.servers:
                mcp_context["serena"] = {
                    "available": True,
                    "capabilities": ["analyze_code", "security_scan", "performance_review"]
                }

            return mcp_context

        except Exception as e:
            print(f"Warning: Failed to get MCP context: {e}")
            return {}

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

    async def _update_metrics(self, result: TaskResult, task_spec: TaskSpec):
        """Update internal metrics."""
        # In a real implementation, this would update monitoring systems
        pass

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
            print(f"Invalid phase: {target_phase}")
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
            "tasks_completed": self.task_count,
            "errors_count": self.error_count,
            "task_metrics": task_metrics,
            "context_cache_stats": self.context_manager.get_cache_stats(),
            "initialization_time": self.startup_time.isoformat() if self.startup_time else None
        }

    async def shutdown(self):
        """Shutdown TeamLeader and cleanup resources."""
        if not self.initialized:
            return

        print("Shutting down TeamLeader...")

        try:
            # Shutdown subsystems
            if self.task_orchestrator:
                await self.task_orchestrator.shutdown()

            await self.context_manager.cleanup()

            # Reset state
            self.initialized = False
            self.startup_time = None

            print("TeamLeader shutdown complete")

        except Exception as e:
            print(f"Error during shutdown: {e}")

    async def get_available_agents(self) -> List[Dict[str, Any]]:
        """Get list of available agents and their capabilities."""
        if not self.agent_registry:
            return []

        try:
            agents = await self.agent_registry.get_all_agents()
            return [
                {
                    "agent_id": agent.agent_id,
                    "agent_type": agent.agent_type,
                    "status": agent.status,
                    "capabilities": agent.capabilities,
                    "current_load": getattr(agent, 'current_load', 0),
                    "last_heartbeat": agent.last_heartbeat.isoformat() if agent.last_heartbeat else None
                }
                for agent in agents
            ]
        except Exception as e:
            print(f"Error getting available agents: {e}")
            return []

    async def get_task_queue_status(self) -> Dict[str, Any]:
        """Get current task queue status."""
        if not self.task_orchestrator:
            return {}

        return {
            "active_tasks": self.task_orchestrator.get_active_tasks(),
            "recent_tasks": self.task_orchestrator.get_task_history(limit=20),
            "metrics": self.task_orchestrator.get_metrics()
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
        # Initialize (without dependencies for standalone mode)
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