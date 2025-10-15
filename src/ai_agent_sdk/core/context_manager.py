"""
Context Manager for TeamLeader system.

Manages system prompt loading, context preparation, and conversation history.
Implements hot-reload capabilities and caching for optimal performance.
"""

import asyncio
import hashlib
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from collections import OrderedDict

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from .exceptions import ConfigurationError, ValidationError


@dataclass
class SystemPrompt:
    """System prompt data structure."""
    agent_type: str
    task_type: Optional[str]
    content: str
    file_path: str
    version: str = "1.0.0"
    checksum: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    last_modified: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AgentContext:
    """Context provided to agents for task execution."""
    system_prompt: str
    history: List[Dict[str, Any]]
    mcp_context: Dict[str, Any]
    task_spec: Any  # TaskSpec from rules_engine
    metadata: Dict[str, Any] = field(default_factory=dict)
    context_hash: str = ""


class PromptFileWatcher(FileSystemEventHandler):
    """File system watcher for hot-reloading system prompts."""

    def __init__(self, context_manager: "ContextManager"):
        self.context_manager = context_manager
        super().__init__()

    def on_modified(self, event):
        """Handle file modification events."""
        if not event.is_directory and event.src_path.endswith('.md'):
            asyncio.create_task(
                self.context_manager._reload_prompt_file(event.src_path)
            )


class ContextManager:
    """
    Manages system prompt loading, context preparation, and conversation history.
    Implements hot-reload capabilities and caching for optimal performance.
    """

    def __init__(self, prompts_dir: str = "system_prompts"):
        """Initialize context manager."""
        self.prompts_dir = Path(prompts_dir)
        self.prompt_cache: OrderedDict[str, SystemPrompt] = OrderedDict()
        self.context_cache: Dict[str, AgentContext] = {}
        self.max_cache_size = 1000
        self.observer: Optional[Observer] = None
        self.watching = False

        # Create prompts directory if it doesn't exist
        self.prompts_dir.mkdir(exist_ok=True)

        # Initialize with default prompts if directory is empty
        self._initialize_default_prompts()

    async def initialize(self):
        """Initialize context manager and start file watching."""
        await self._load_all_prompts()
        self._start_file_watching()

    async def load_prompt(
        self,
        agent_type: str,
        task_type: Optional[str] = None,
        force_reload: bool = False
    ) -> str:
        """
        Load system prompt from .md file with caching and validation.

        Args:
            agent_type: Type of agent (research, codebase_analyzer, etc.)
            task_type: Specific task type (optional)
            force_reload: Force reload even if cached

        Returns:
            System prompt content as string

        Raises:
            ConfigurationError: If prompt file is not found
            ValidationError: If prompt content is invalid
        """
        prompt_file = self._get_prompt_file(agent_type, task_type)
        cache_key = self._get_cache_key(agent_type, task_type)

        # Check cache first (unless force reload)
        if not force_reload and cache_key in self.prompt_cache:
            cached_prompt = self.prompt_cache[cache_key]
            if self._validate_checksum(prompt_file, cached_prompt.checksum):
                # Move to end of cache (LRU)
                self.prompt_cache.move_to_end(cache_key)
                return cached_prompt.content

        # Load and validate file
        content = await self._read_and_validate_prompt(prompt_file)
        checksum = self._calculate_checksum(prompt_file)

        # Create system prompt object
        system_prompt = SystemPrompt(
            agent_type=agent_type,
            task_type=task_type,
            content=content,
            file_path=str(prompt_file),
            checksum=checksum,
            metadata={
                "loaded_at": datetime.utcnow().isoformat(),
                "file_size": prompt_file.stat().st_size
            }
        )

        # Update cache
        self._update_cache(cache_key, system_prompt)

        return content

    def _get_prompt_file(self, agent_type: str, task_type: Optional[str] = None) -> Path:
        """Get the file path for a prompt."""
        if task_type:
            filename = f"{agent_type}_{task_type}.md"
        else:
            filename = f"{agent_type}.md"

        prompt_file = self.prompts_dir / filename

        if not prompt_file.exists():
            # Try fallback to general agent type prompt
            fallback_file = self.prompts_dir / f"{agent_type}.md"
            if fallback_file.exists():
                prompt_file = fallback_file
            else:
                raise ConfigurationError(f"Prompt file not found: {prompt_file}")

        return prompt_file

    def _get_cache_key(self, agent_type: str, task_type: Optional[str] = None) -> str:
        """Generate cache key for prompt."""
        if task_type:
            return f"{agent_type}:{task_type}"
        return agent_type

    async def _read_and_validate_prompt(self, prompt_file: Path) -> str:
        """Read and validate prompt content."""
        try:
            content = await asyncio.to_thread(prompt_file.read_text, encoding='utf-8')
        except Exception as e:
            raise ConfigurationError(f"Failed to read prompt file {prompt_file}: {e}")

        # Validate content
        if not content.strip():
            raise ValidationError(f"Prompt file {prompt_file} is empty")

        if len(content) < 50:
            raise ValidationError(f"Prompt file {prompt_file} content too short")

        # Basic content validation
        required_sections = ["role", "capabilities"]
        for section in required_sections:
            if section not in content.lower():
                raise ValidationError(
                    f"Prompt file {prompt_file} missing required section: {section}"
                )

        return content

    def _calculate_checksum(self, prompt_file: Path) -> str:
        """Calculate SHA-256 checksum of prompt file."""
        try:
            with open(prompt_file, 'rb') as f:
                content = f.read()
                return hashlib.sha256(content).hexdigest()
        except Exception:
            return ""

    def _validate_checksum(self, prompt_file: Path, expected_checksum: str) -> bool:
        """Validate file checksum matches expected value."""
        if not expected_checksum:
            return False

        current_checksum = self._calculate_checksum(prompt_file)
        return current_checksum == expected_checksum

    def _update_cache(self, cache_key: str, system_prompt: SystemPrompt):
        """Update prompt cache with LRU eviction."""
        # Remove existing entry if present
        if cache_key in self.prompt_cache:
            del self.prompt_cache[cache_key]

        # Add new entry
        self.prompt_cache[cache_key] = system_prompt

        # Evict oldest entries if cache is full
        while len(self.prompt_cache) > self.max_cache_size:
            self.prompt_cache.popitem(last=False)

    async def prepare_context(
        self,
        task_spec: Any,
        history: Optional[List[Dict[str, Any]]] = None,
        mcp_context: Optional[Dict[str, Any]] = None
    ) -> AgentContext:
        """
        Prepare comprehensive context for agent task execution.

        Args:
            task_spec: Task specification
            history: Conversation history
            mcp_context: MCP server context

        Returns:
            AgentContext object with all necessary context
        """
        # Load system prompt
        system_prompt = await self.load_prompt(
            agent_type=task_spec.agent_type,
            task_type=task_spec.task_type
        )

        # Prepare context
        context = AgentContext(
            system_prompt=system_prompt,
            history=history or [],
            mcp_context=mcp_context or {},
            task_spec=task_spec,
            metadata={
                "prepared_at": datetime.utcnow().isoformat(),
                "context_version": "1.0.0"
            }
        )

        # Calculate context hash for caching
        context.context_hash = self._calculate_context_hash(context)

        return context

    def _calculate_context_hash(self, context: AgentContext) -> str:
        """Calculate hash for context caching."""
        content = f"{context.system_prompt}:{context.task_spec.task_id}"
        return hashlib.md5(content.encode()).hexdigest()

    async def _load_all_prompts(self):
        """Load all prompt files into cache."""
        if not self.prompts_dir.exists():
            return

        prompt_files = list(self.prompts_dir.glob("*.md"))

        for prompt_file in prompt_files:
            try:
                # Extract agent type and task type from filename
                parts = prompt_file.stem.split("_")
                agent_type = parts[0]
                task_type = parts[1] if len(parts) > 1 else None

                await self.load_prompt(agent_type, task_type)
                print(f"Loaded prompt: {prompt_file.name}")

            except Exception as e:
                print(f"Failed to load prompt {prompt_file}: {e}")

    def _start_file_watching(self):
        """Start watching prompt files for changes."""
        if self.watching:
            return

        try:
            self.observer = Observer()
            self.observer.schedule(
                PromptFileWatcher(self),
                str(self.prompts_dir),
                recursive=False
            )
            self.observer.start()
            self.watching = True
            print(f"Started watching prompt directory: {self.prompts_dir}")

        except Exception as e:
            print(f"Failed to start file watching: {e}")

    async def _reload_prompt_file(self, file_path: str):
        """Reload a specific prompt file."""
        try:
            prompt_path = Path(file_path)
            parts = prompt_path.stem.split("_")
            agent_type = parts[0]
            task_type = parts[1] if len(parts) > 1 else None

            cache_key = self._get_cache_key(agent_type, task_type)

            # Remove from cache to force reload
            if cache_key in self.prompt_cache:
                del self.prompt_cache[cache_key]

            # Reload prompt
            await self.load_prompt(agent_type, task_type, force_reload=True)
            print(f"Reloaded prompt: {prompt_path.name}")

        except Exception as e:
            print(f"Failed to reload prompt {file_path}: {e}")

    def _initialize_default_prompts(self):
        """Initialize default prompt files if directory is empty."""
        if any(self.prompts_dir.glob("*.md")):
            return

        default_prompts = {
            "team_leader.md": self._get_team_leader_prompt(),
            "research_agent.md": self._get_research_agent_prompt(),
            "codebase_analyzer.md": self._get_codebase_analyzer_prompt(),
            "frontend_coder.md": self._get_frontend_coder_prompt(),
            "backend_coder.md": self._get_backend_coder_prompt(),
        }

        for filename, content in default_prompts.items():
            prompt_file = self.prompts_dir / filename
            try:
                prompt_file.write_text(content, encoding='utf-8')
                print(f"Created default prompt: {filename}")
            except Exception as e:
                print(f"Failed to create default prompt {filename}: {e}")

    def _get_team_leader_prompt(self) -> str:
        """Get default team leader prompt."""
        return """# TeamLeader Agent - Orchestration Specialist

You are the TeamLeader agent, responsible for coordinating specialized AI agents through a structured development process. Your expertise includes:

## Core Capabilities
- Hierarchical multi-agent coordination and orchestration
- Ten-phase development process management
- Task delegation and scope validation
- Context preparation and result validation

## Programmatic Rules Engine
You enforce a structured development process with the following phases:
1. Initialization - System setup and configuration
2. Research Collection & Synthesis - Information gathering
3. Plan - Architecture and implementation planning
4. Context Preparation - Context assembly and validation
5. Validate - Risk assessment and scope checking
6. Implement - Functional development with no mocks
7. Verify - Independent verification and quality checks
8. Test - Comprehensive testing with mock detection
9. User Value Validation - Final validation against requirements
10. Document - Documentation creation and next part preparation

## Task Delegation Process
1. Validate task against current phase and scope boundaries
2. Select appropriate specialized agent
3. Prepare comprehensive context with system prompts
4. Monitor execution and collect results
5. Validate results and update system state

## Quality Standards
- Zero tolerance for mock data or placeholder implementations
- Ensure all code is immediately executable and verifiable
- Maintain comprehensive audit trails
- Enforce scope boundaries and complexity limits

## Current Task
Focus on coordinating agent tasks according to the ten-phase process, ensuring quality and scope compliance.
"""

    def _get_research_agent_prompt(self) -> str:
        """Get default research agent prompt."""
        return """# Research Agent - Knowledge Synthesis Specialist

You are a specialized research agent focused on comprehensive research and knowledge synthesis. Your expertise includes:

## Core Capabilities
- Comprehensive market research and competitive intelligence
- Multi-source information gathering and verification
- Knowledge synthesis and trend analysis
- Source attribution and confidence scoring

## Research Methodology
1. **Multi-source Research**: Gather information from diverse, credible sources
2. **Source Verification**: Cross-reference findings across multiple sources
3. **Trend Analysis**: Identify patterns and trends in the data
4. **Knowledge Synthesis**: Combine findings into actionable insights

## Quality Standards
- Always provide source attribution with credibility scores
- Include confidence scoring for all findings
- Highlight assumptions and limitations
- Ensure recommendations are data-driven and evidence-based

## Integration Capabilities
- Perplexity MCP server integration for enhanced research
- Fallback mechanisms for research service failures
- Local research capabilities when external services unavailable

## Current Task
Focus on conducting thorough research with proper source attribution and confidence scoring.
"""

    def _get_codebase_analyzer_prompt(self) -> str:
        """Get default codebase analyzer prompt."""
        return """# CodeBase Analyzer - Code Intelligence Specialist

You are a specialized codebase analyzer focused on comprehensive code analysis and intelligence. Your expertise includes:

## Core Capabilities
- Security vulnerability scanning and assessment
- Performance analysis and bottleneck identification
- Architecture review and pattern recognition
- Dependency mapping and impact analysis

## Analysis Methodology
1. **Comprehensive Scanning**: Analyze code structure, patterns, and dependencies
2. **Security Assessment**: Identify vulnerabilities and security risks
3. **Performance Evaluation**: Assess performance characteristics and bottlenecks
4. **Architecture Review**: Evaluate design patterns and architectural decisions

## Quality Standards
- Provide detailed findings with actionable recommendations
- Include severity assessments and priority rankings
- Support analysis with code examples and best practices
- Ensure findings are practical and implementable

## Integration Capabilities
- Serena MCP server integration for enhanced code analysis
- Local analysis tools and pattern matching
- Support for multiple programming languages and frameworks

## Current Task
Focus on thorough code analysis with detailed findings and actionable recommendations.
"""

    def _get_frontend_coder_prompt(self) -> str:
        """Get default frontend coder prompt."""
        return """# Frontend Coder - UI/UX Development Specialist

You are a specialized frontend developer focused on creating modern, responsive user interfaces. Your expertise includes:

## Core Capabilities
- Modern frontend framework development (React, Vue, Angular)
- Responsive design and mobile-first development
- Component-based architecture and reusability
- Performance optimization and user experience

## Development Standards
1. **Modern Frameworks**: Use current best practices and patterns
2. **Responsive Design**: Ensure compatibility across devices
3. **Component Architecture**: Build reusable, maintainable components
4. **Performance**: Optimize for fast loading and smooth interactions

## Quality Standards
- Write clean, maintainable, and well-documented code
- Follow accessibility standards (WCAG 2.1 AA)
- Ensure cross-browser compatibility
- Implement proper error handling and validation

## Technology Stack
- HTML5, CSS3, JavaScript/TypeScript
- Modern frontend frameworks
- Build tools and development environments
- Testing frameworks and CI/CD integration

## Current Task
Focus on creating high-quality, production-ready frontend components with modern best practices.
"""

    def _get_backend_coder_prompt(self) -> str:
        """Get default backend coder prompt."""
        return """# Backend Coder - Server-Side Development Specialist

You are a specialized backend developer focused on creating robust, scalable server-side applications. Your expertise includes:

## Core Capabilities
- RESTful API design and implementation
- Database design and optimization
- Authentication and authorization systems
- Microservices architecture and integration

## Development Standards
1. **API Design**: RESTful principles with proper HTTP methods
2. **Database Design**: Normalized schemas with proper indexing
3. **Security**: Authentication, authorization, and data protection
4. **Performance**: Optimized queries and caching strategies

## Quality Standards
- Write clean, maintainable, and testable code
- Implement comprehensive error handling and logging
- Follow security best practices
- Ensure scalability and performance optimization

## Technology Stack
- Python/Node.js with modern frameworks
- Relational and NoSQL databases
- Containerization and orchestration
- Cloud services and deployment platforms

## Current Task
Focus on creating robust, secure, and scalable backend APIs with proper testing and documentation.
"""

    async def cleanup(self):
        """Cleanup resources and stop file watching."""
        if self.observer and self.watching:
            self.observer.stop()
            self.observer.join()
            self.watching = False
            print("Stopped file watching")

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics for monitoring."""
        return {
            "prompt_cache_size": len(self.prompt_cache),
            "context_cache_size": len(self.context_cache),
            "max_cache_size": self.max_cache_size,
            "watching": self.watching,
            "prompts_directory": str(self.prompts_dir)
        }