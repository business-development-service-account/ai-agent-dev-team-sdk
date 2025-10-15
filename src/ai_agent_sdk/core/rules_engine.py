"""
Rules Engine for TeamLeader orchestration.

Implements the programmatic rules engine that enforces the ten-phase
development process with validation gates and scope enforcement.
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass
from enum import Enum

from .exceptions import ScopeViolationError, ConfigurationError


class Phase(Enum):
    """Development phases in the ten-phase process."""
    INITIALIZATION = "initialization"
    RESEARCH = "research"
    PLANNING = "planning"
    CONTEXT_PREPARATION = "context_preparation"
    VALIDATION = "validation"
    IMPLEMENTATION = "implementation"
    VERIFICATION = "verification"
    TESTING = "testing"
    USER_VALUE_VALIDATION = "user_value_validation"
    DOCUMENTATION = "documentation"
    PREPARATION = "preparation"


@dataclass
class PhaseConfig:
    """Configuration for a development phase."""
    name: str
    allowed_tasks: Set[str]
    completion_criteria: List[str]
    max_complexity: int
    timeout_seconds: int


@dataclass
class TaskSpec:
    """Task specification for validation."""
    task_id: str
    agent_type: str
    task_type: str
    task: str
    complexity: int
    priority: int
    project_id: Optional[str] = None
    metadata: Dict[str, Any] = None


class RulesEngine:
    """
    Programmatic rules engine implementing the ten-phase development process
    with validation gates and scope enforcement.
    """

    def __init__(self, rules_config: Dict[str, Any]):
        """Initialize rules engine with configuration."""
        self.config = rules_config
        self.current_phase = Phase.INITIALIZATION
        self.phase_history: List[Phase] = []
        self.complexity_budget = rules_config.get("complexity_budget", 25)
        self.current_complexity_used = 0
        self.phase_configs = self._load_phase_configs()
        self.agent_registry: Dict[str, Set[str]] = {}
        self.task_history: List[Dict[str, Any]] = []

        # Add phases attribute for backward compatibility
        self.phases = list(Phase)
    def _load_phase_configs(self) -> Dict[Phase, PhaseConfig]:
        """Load phase configurations from rules config."""
        default_configs = {
            Phase.INITIALIZATION: PhaseConfig(
                name="Initialization",
                allowed_tasks={"system_setup", "configuration", "validation"},
                completion_criteria=["team_leader_operational", "subsystems_initialized"],
                max_complexity=3,
                timeout_seconds=300
            ),
            Phase.RESEARCH: PhaseConfig(
                name="Research Collection & Synthesis",
                allowed_tasks={"research", "analysis", "knowledge_synthesis"},
                completion_criteria=["research_completed", "findings_synthesized"],
                max_complexity=8,
                timeout_seconds=1800
            ),
            Phase.PLANNING: PhaseConfig(
                name="Plan",
                allowed_tasks={"architecture", "design", "planning"},
                completion_criteria=["implementation_plan_created", "architecture_approved"],
                max_complexity=7,
                timeout_seconds=1200
            ),
            Phase.CONTEXT_PREPARATION: PhaseConfig(
                name="Context Preparation",
                allowed_tasks={"context_assembly", "validation", "documentation"},
                completion_criteria=["context_prepared", "validation_passed"],
                max_complexity=5,
                timeout_seconds=600
            ),
            Phase.VALIDATION: PhaseConfig(
                name="Validate",
                allowed_tasks={"validation", "risk_assessment", "scope_check"},
                completion_criteria=["mock_risk_assessed", "scope_validated"],
                max_complexity=6,
                timeout_seconds=900
            ),
            Phase.IMPLEMENTATION: PhaseConfig(
                name="Implement",
                allowed_tasks={"development", "coding", "implementation"},
                completion_criteria=["functional_implementation", "no_mocks"],
                max_complexity=10,
                timeout_seconds=3600
            ),
            Phase.VERIFICATION: PhaseConfig(
                name="Verify",
                allowed_tasks={"verification", "testing", "quality_check"},
                completion_criteria=["independent_verification", "features_match_plan"],
                max_complexity=8,
                timeout_seconds=1800
            ),
            Phase.TESTING: PhaseConfig(
                name="Test",
                allowed_tasks={"testing", "qa", "integration_testing"},
                completion_criteria=["comprehensive_testing", "no_mocks_detected"],
                max_complexity=9,
                timeout_seconds=2400
            ),
            Phase.USER_VALUE_VALIDATION: PhaseConfig(
                name="User Value Validation",
                allowed_tasks={"validation", "user_testing", "compliance_check"},
                completion_criteria=["value_delivered", "technical_compliance"],
                max_complexity=7,
                timeout_seconds=1200
            ),
            Phase.DOCUMENTATION: PhaseConfig(
                name="Document",
                allowed_tasks={"documentation", "guides", "api_docs"},
                completion_criteria=["documentation_created", "approved_features_only"],
                max_complexity=5,
                timeout_seconds=900
            ),
            Phase.PREPARATION: PhaseConfig(
                name="Prepare",
                allowed_tasks={"preparation", "setup", "configuration"},
                completion_criteria=["next_part_ready", "cleanup_completed"],
                max_complexity=3,
                timeout_seconds=300
            ),
        }

        # Override with custom configs if provided
        custom_configs = self.config.get("phases", {})
        for phase_name, config in custom_configs.items():
            try:
                phase_enum = Phase(phase_name.lower())
                default_configs[phase_enum] = PhaseConfig(
                    name=config.get("name", phase_name),
                    allowed_tasks=set(config.get("allowed_tasks", [])),
                    completion_criteria=config.get("completion_criteria", []),
                    max_complexity=config.get("max_complexity", 5),
                    timeout_seconds=config.get("timeout_seconds", 600)
                )
            except ValueError:
                raise ConfigurationError(f"Invalid phase name: {phase_name}")

        return default_configs

    def validate_scope(self, task_spec: TaskSpec) -> bool:
        """
        Validate task against current scope boundaries.

        Args:
            task_spec: Task specification to validate

        Returns:
            True if task is within scope, False otherwise

        Raises:
            ScopeViolationError: If task exceeds scope boundaries
        """
        # Check phase-appropriate tasks
        phase_config = self.phase_configs[self.current_phase]
        if task_spec.task_type not in phase_config.allowed_tasks:
            raise ScopeViolationError(
                f"Task type '{task_spec.task_type}' not allowed in phase "
                f"'{self.current_phase.value}'. Allowed tasks: "
                f"{phase_config.allowed_tasks}"
            )

        # Check complexity budget
        if self.current_complexity_used + task_spec.complexity > self.complexity_budget:
            raise ScopeViolationError(
                f"Task complexity {task_spec.complexity} exceeds remaining budget. "
                f"Current used: {self.current_complexity_used}, "
                f"Budget: {self.complexity_budget}, "
                f"Remaining: {self.complexity_budget - self.current_complexity_used}"
            )

        # Check task complexity against phase limits
        if task_spec.complexity > phase_config.max_complexity:
            raise ScopeViolationError(
                f"Task complexity {task_spec.complexity} exceeds phase maximum "
                f"of {phase_config.max_complexity} for phase {self.current_phase.value}"
            )

        # Check agent availability
        if not self._agent_available(task_spec.agent_type):
            raise ScopeViolationError(
                f"Agent type '{task_spec.agent_type}' not available for task "
                f"'{task_spec.task_type}'"
            )

        return True

    def _agent_available(self, agent_type: str) -> bool:
        """Check if agent type is available and capable."""
        if agent_type not in self.agent_registry:
            return False

        # In a real implementation, this would check agent health, load, etc.
        return True

    def can_progress_to_phase(self, target_phase: Phase) -> bool:
        """
        Check if progression to target phase is allowed.

        Args:
            target_phase: Target phase to progress to

        Returns:
            True if progression is allowed, False otherwise
        """
        # Check if we're following the correct sequence
        expected_next_phase = self._get_next_phase(self.current_phase)
        if target_phase != expected_next_phase:
            return False

        # Check current phase completion criteria
        current_config = self.phase_configs[self.current_phase]
        for criterion in current_config.completion_criteria:
            if not self._check_requirement(criterion):
                return False

        return True

    def _get_next_phase(self, current_phase: Phase) -> Optional[Phase]:
        """Get the next phase in the sequence."""
        phase_order = list(Phase)
        current_index = phase_order.index(current_phase)

        if current_index < len(phase_order) - 1:
            return phase_order[current_index + 1]

        return None

    def _check_requirement(self, requirement: str) -> bool:
        """
        Check if a specific requirement is met.

        In a real implementation, this would check actual system state,
        task completion, validation results, etc.
        """
        # For now, return True - in real implementation, check actual requirements
        return True

    async def progress_to_phase(self, target_phase: Phase) -> bool:
        """
        Progress to the next phase if requirements are met.

        Args:
            target_phase: Target phase to progress to

        Returns:
            True if progression successful, False otherwise
        """
        if not self.can_progress_to_phase(target_phase):
            return False

        # Update phase history and current phase
        self.phase_history.append(self.current_phase)
        self.current_phase = target_phase

        # Log phase progression
        self._log_phase_progression(self.current_phase, target_phase)

        return True

    def _log_phase_progression(self, from_phase: Phase, to_phase: Phase):
        """Log phase progression for audit purposes."""
        progression_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "from_phase": from_phase.value,
            "to_phase": to_phase.value,
            "complexity_used": self.current_complexity_used,
            "task_count": len(self.task_history)
        }

        # In a real implementation, this would be logged to audit system
        print(f"Phase progression: {from_phase.value} -> {to_phase.value}")

    def register_task_execution(self, task_spec: TaskSpec, result: Dict[str, Any]):
        """Register task execution for tracking."""
        self.current_complexity_used += task_spec.complexity

        task_entry = {
            "task_id": task_spec.task_id,
            "agent_type": task_spec.agent_type,
            "task_type": task_spec.task_type,
            "complexity": task_spec.complexity,
            "phase": self.current_phase.value,
            "timestamp": datetime.utcnow().isoformat(),
            "result": result
        }

        self.task_history.append(task_entry)

    def get_phase_status(self) -> Dict[str, Any]:
        """Get current phase status and metrics."""
        phase_config = self.phase_configs[self.current_phase]

        return {
            "current_phase": self.current_phase.value,
            "phase_name": phase_config.name,
            "complexity_budget": self.complexity_budget,
            "complexity_used": self.current_complexity_used,
            "complexity_remaining": self.complexity_budget - self.current_complexity_used,
            "tasks_completed": len(self.task_history),
            "phase_progress": self._calculate_phase_progress(),
            "can_progress": self.can_progress_to_phase(self._get_next_phase(self.current_phase) or self.current_phase)
        }

    def _calculate_phase_progress(self) -> float:
        """Calculate progress percentage for current phase."""
        current_config = self.phase_configs[self.current_phase]
        completed_criteria = sum(
            1 for criterion in current_config.completion_criteria
            if self._check_requirement(criterion)
        )

        if not current_config.completion_criteria:
            return 0.0

        return completed_criteria / len(current_config.completion_criteria)

    def reset_complexity_budget(self):
        """Reset complexity budget (for new project/part)."""
        self.current_complexity_used = 0
        self.task_history.clear()

    def add_agent_capability(self, agent_type: str, task_types: Set[str]):
        """Add agent capability to registry."""
        if agent_type not in self.agent_registry:
            self.agent_registry[agent_type] = set()
        self.agent_registry[agent_type].update(task_types)