"""
Task Orchestrator for TeamLeader system.

Handles task delegation, execution monitoring, and result collection.
Coordinates with specialized agents and manages task lifecycle.
"""

import asyncio
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from contextlib import asynccontextmanager

from .exceptions import TaskExecutionError, AgentUnavailableError, TimeoutError
from .rules_engine import TaskSpec
from .context_manager import AgentContext


class TaskStatus(Enum):
    """Task execution status."""
    PENDING = "pending"
    DELEGATED = "delegated"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class TaskPriority(Enum):
    """Task priority levels."""
    LOW = 1
    MEDIUM = 5
    HIGH = 7
    CRITICAL = 10


@dataclass
class TaskResult:
    """Result from agent task execution."""
    task_id: str
    agent_id: str
    status: TaskStatus
    content: str
    execution_time: float
    confidence_score: float
    sources: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class TaskExecution:
    """Task execution tracking data."""
    task_id: str
    task_spec: TaskSpec
    agent_id: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    context: Optional[AgentContext] = None
    result: Optional[TaskResult] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    timeout_at: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3
    execution_metadata: Dict[str, Any] = field(default_factory=dict)


class TaskMonitor:
    """Context manager for monitoring task execution."""

    def __init__(self, task_id: str, task_spec: TaskSpec, orchestrator: "TaskOrchestrator"):
        self.task_id = task_id
        self.task_spec = task_spec
        self.orchestrator = orchestrator
        self.start_time: Optional[float] = None
        self.execution: Optional[TaskExecution] = None

    async def __aenter__(self):
        """Start task execution monitoring."""
        self.start_time = time.time()
        self.execution = self.orchestrator._create_task_execution(self.task_id, self.task_spec)
        await self.orchestrator._start_task_execution(self.execution)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """End task execution monitoring."""
        if self.execution:
            execution_time = time.time() - self.start_time if self.start_time else 0

            if exc_type:
                await self.orchestrator._fail_task_execution(
                    self.execution, exc_type, exc_val, execution_time
                )
            else:
                await self.orchestrator._complete_task_execution(self.execution, execution_time)

    async def update_progress(self, progress: float, message: str = ""):
        """Update task progress."""
        if self.execution:
            self.execution.execution_metadata["progress"] = progress
            self.execution.execution_metadata["progress_message"] = message
            self.execution.execution_metadata["last_update"] = datetime.utcnow().isoformat()

    async def log_event(self, event_type: str, data: Dict[str, Any]):
        """Log execution event."""
        if self.execution:
            if "events" not in self.execution.execution_metadata:
                self.execution.execution_metadata["events"] = []

            event = {
                "type": event_type,
                "timestamp": datetime.utcnow().isoformat(),
                "data": data
            }
            self.execution.execution_metadata["events"].append(event)


class TaskOrchestrator:
    """
    Handles task delegation, execution monitoring, and result collection.
    Coordinates with specialized agents and manages task lifecycle.
    """

    def __init__(self, agent_registry, context_manager, mcp_client, config: Dict[str, Any]):
        """Initialize task orchestrator."""
        self.agent_registry = agent_registry
        self.context_manager = context_manager
        self.mcp_client = mcp_client
        self.config = config

        # Task execution tracking
        self.active_tasks: Dict[str, TaskExecution] = {}
        self.task_history: List[TaskExecution] = []
        self.task_queue: asyncio.Queue = asyncio.Queue()

        # Configuration
        self.max_concurrent_tasks = config.get("max_concurrent_tasks", 10)
        self.default_timeout = config.get("default_timeout", 300)  # 5 minutes
        self.task_timeout_check_interval = config.get("timeout_check_interval", 30)

        # Background tasks
        self._running = False
        self._background_tasks: List[asyncio.Task] = []

    async def initialize(self):
        """Initialize task orchestrator and start background tasks."""
        self._running = True
        await self._start_background_tasks()

    async def shutdown(self):
        """Shutdown task orchestrator and cleanup resources."""
        self._running = False

        # Cancel background tasks
        for task in self._background_tasks:
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

        # Cancel active tasks
        for task_id, execution in self.active_tasks.items():
            execution.status = TaskStatus.CANCELLED

        print("Task orchestrator shutdown complete")

    async def _start_background_tasks(self):
        """Start background monitoring tasks."""
        # Task processor
        processor_task = asyncio.create_task(self._task_processor())
        self._background_tasks.append(processor_task)

        # Timeout checker
        timeout_task = asyncio.create_task(self._timeout_checker())
        self._background_tasks.append(timeout_task)

    @asynccontextmanager
    async def task_monitor(self, task_spec: TaskSpec):
        """Create task monitor for execution tracking."""
        task_id = str(uuid.uuid4())
        async with TaskMonitor(task_id, task_spec, self) as monitor:
            yield monitor

    async def execute_task(
        self,
        task_spec: TaskSpec,
        context: Optional[AgentContext] = None,
        timeout: Optional[int] = None
    ) -> TaskResult:
        """
        Execute a task with the appropriate agent.

        Args:
            task_spec: Task specification
            context: Agent context (optional)
            timeout: Task timeout in seconds (optional)

        Returns:
            TaskResult with execution results

        Raises:
            TaskExecutionError: If task execution fails
            AgentUnavailableError: If required agent is not available
            TimeoutError: If task execution times out
        """
        # Generate task ID
        task_id = str(uuid.uuid4())

        # Prepare context if not provided
        if not context:
            context = await self.context_manager.prepare_context(task_spec)

        # Create task execution record
        execution = self._create_task_execution(task_id, task_spec, context)
        execution.timeout_at = datetime.utcnow() + timedelta(
            seconds=timeout or self.default_timeout
        )

        # Select agent
        agent = await self._select_agent(task_spec)
        if not agent:
            raise AgentUnavailableError(
                f"No available agent for task type: {task_spec.agent_type}"
            )

        execution.agent_id = agent.agent_id

        try:
            # Start execution
            await self._start_task_execution(execution)

            # Execute task
            result = await self._execute_with_agent(
                agent, task_spec, context, timeout or self.default_timeout
            )

            # Complete execution
            await self._complete_task_execution(execution, result.execution_time)

            return result

        except Exception as e:
            await self._fail_task_execution(execution, type(e), str(e))
            raise TaskExecutionError(f"Task execution failed: {e}") from e

        finally:
            # Cleanup
            if task_id in self.active_tasks:
                del self.active_tasks[task_id]

    def _create_task_execution(
        self,
        task_id: str,
        task_spec: TaskSpec,
        context: Optional[AgentContext] = None
    ) -> TaskExecution:
        """Create task execution record."""
        execution = TaskExecution(
            task_id=task_id,
            task_spec=task_spec,
            context=context
        )

        self.active_tasks[task_id] = execution
        return execution

    async def _select_agent(self, task_spec: TaskSpec):
        """Select appropriate agent for task execution."""
        return await self.agent_registry.get_best_agent(
            task_spec.agent_type,
            task_spec.task_type,
            task_spec.complexity
        )

    async def _start_task_execution(self, execution: TaskExecution):
        """Start task execution tracking."""
        execution.status = TaskStatus.IN_PROGRESS
        execution.started_at = datetime.utcnow()

        print(f"Started task execution: {execution.task_id} -> {execution.agent_id}")

    async def _execute_with_agent(
        self,
        agent,
        task_spec: TaskSpec,
        context: AgentContext,
        timeout: int
    ) -> TaskResult:
        """Execute task with specific agent."""
        start_time = time.time()

        try:
            # Execute via agent
            result = await asyncio.wait_for(
                agent.execute_task(task_spec, context),
                timeout=timeout
            )

            execution_time = time.time() - start_time

            # Ensure result has required fields
            if not isinstance(result, TaskResult):
                result = TaskResult(
                    task_id=task_spec.task_id,
                    agent_id=agent.agent_id,
                    status=TaskStatus.COMPLETED,
                    content=str(result),
                    execution_time=execution_time,
                    confidence_score=0.8  # Default confidence
                )

            return result

        except asyncio.TimeoutError:
            execution_time = time.time() - start_time
            raise TimeoutError(f"Task execution timed out after {timeout} seconds")

    async def _complete_task_execution(
        self,
        execution: TaskExecution,
        execution_time: float
    ):
        """Complete task execution successfully."""
        execution.status = TaskStatus.COMPLETED
        execution.completed_at = datetime.utcnow()

        # Move to history
        self.task_history.append(execution)

        print(f"Completed task execution: {execution.task_id} in {execution_time:.2f}s")

    async def _fail_task_execution(
        self,
        execution: TaskExecution,
        exc_type: type,
        exc_val: Any,
        execution_time: Optional[float] = None
    ):
        """Mark task execution as failed."""
        execution.status = TaskStatus.FAILED
        execution.completed_at = datetime.utcnow()
        execution.execution_metadata["error_type"] = exc_type.__name__
        execution.execution_metadata["error_message"] = str(exc_val)

        # Move to history
        self.task_history.append(execution)

        print(f"Failed task execution: {execution.task_id} - {exc_type.__name__}: {exc_val}")

    async def _task_processor(self):
        """Background task to process queued tasks."""
        while self._running:
            try:
                # Wait for task with timeout
                task_data = await asyncio.wait_for(
                    self.task_queue.get(),
                    timeout=1.0
                )

                # Process task
                await self._process_queued_task(task_data)

            except asyncio.TimeoutError:
                # No tasks in queue, continue
                continue
            except Exception as e:
                print(f"Error processing queued task: {e}")

    async def _process_queued_task(self, task_data: Dict[str, Any]):
        """Process a queued task."""
        try:
            task_spec = task_data["task_spec"]
            callback = task_data.get("callback")

            # Execute task
            result = await self.execute_task(task_spec)

            # Call callback if provided
            if callback:
                await callback(result)

        except Exception as e:
            print(f"Error processing queued task {task_data.get('task_id')}: {e}")

    async def _timeout_checker(self):
        """Background task to check for task timeouts."""
        while self._running:
            try:
                await asyncio.sleep(self.task_timeout_check_interval)
                await self._check_timeouts()

            except Exception as e:
                print(f"Error in timeout checker: {e}")

    async def _check_timeouts(self):
        """Check for and handle task timeouts."""
        now = datetime.utcnow()
        timed_out_tasks = []

        for task_id, execution in self.active_tasks.items():
            if (execution.timeout_at and now > execution.timeout_at and
                execution.status == TaskStatus.IN_PROGRESS):
                timed_out_tasks.append(task_id)

        # Handle timed out tasks
        for task_id in timed_out_tasks:
            execution = self.active_tasks[task_id]
            await self._fail_task_execution(
                execution,
                TimeoutError,
                f"Task timed out at {execution.timeout_at}"
            )
            del self.active_tasks[task_id]

    async def queue_task(
        self,
        task_spec: TaskSpec,
        callback: Optional[Callable] = None
    ) -> str:
        """
        Queue a task for background execution.

        Args:
            task_spec: Task specification
            callback: Optional callback function for completion

        Returns:
            Task ID for tracking
        """
        task_id = str(uuid.uuid4())

        task_data = {
            "task_id": task_id,
            "task_spec": task_spec,
            "callback": callback,
            "queued_at": datetime.utcnow().isoformat()
        }

        await self.task_queue.put(task_data)

        print(f"Queued task: {task_id}")

        return task_id

    async def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a task execution.

        Args:
            task_id: Task ID to cancel

        Returns:
            True if task was cancelled, False if not found or already completed
        """
        if task_id in self.active_tasks:
            execution = self.active_tasks[task_id]
            execution.status = TaskStatus.CANCELLED
            execution.completed_at = datetime.utcnow()

            # Remove from active tasks
            del self.active_tasks[task_id]

            # Add to history
            self.task_history.append(execution)

            print(f"Cancelled task: {task_id}")
            return True

        return False

    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific task."""
        # Check active tasks
        if task_id in self.active_tasks:
            execution = self.active_tasks[task_id]
            return self._execution_to_dict(execution)

        # Check task history
        for execution in self.task_history:
            if execution.task_id == task_id:
                return self._execution_to_dict(execution)

        return None

    def _execution_to_dict(self, execution: TaskExecution) -> Dict[str, Any]:
        """Convert task execution to dictionary."""
        return {
            "task_id": execution.task_id,
            "agent_id": execution.agent_id,
            "status": execution.status.value,
            "task_type": execution.task_spec.task_type,
            "agent_type": execution.task_spec.agent_type,
            "created_at": execution.created_at.isoformat(),
            "started_at": execution.started_at.isoformat() if execution.started_at else None,
            "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
            "timeout_at": execution.timeout_at.isoformat() if execution.timeout_at else None,
            "retry_count": execution.retry_count,
            "execution_metadata": execution.execution_metadata
        }

    def get_active_tasks(self) -> List[Dict[str, Any]]:
        """Get list of all active tasks."""
        return [
            self._execution_to_dict(execution)
            for execution in self.active_tasks.values()
        ]

    def get_task_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent task history."""
        recent_tasks = self.task_history[-limit:] if limit > 0 else self.task_history
        return [
            self._execution_to_dict(execution)
            for execution in reversed(recent_tasks)
        ]

    def get_metrics(self) -> Dict[str, Any]:
        """Get task orchestrator metrics."""
        total_tasks = len(self.task_history) + len(self.active_tasks)
        completed_tasks = sum(
            1 for execution in self.task_history
            if execution.status == TaskStatus.COMPLETED
        )
        failed_tasks = sum(
            1 for execution in self.task_history
            if execution.status == TaskStatus.FAILED
        )

        return {
            "active_tasks": len(self.active_tasks),
            "queued_tasks": self.task_queue.qsize(),
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "failed_tasks": failed_tasks,
            "success_rate": completed_tasks / total_tasks if total_tasks > 0 else 0,
            "max_concurrent_tasks": self.max_concurrent_tasks,
            "background_tasks_running": len(self._background_tasks)
        }