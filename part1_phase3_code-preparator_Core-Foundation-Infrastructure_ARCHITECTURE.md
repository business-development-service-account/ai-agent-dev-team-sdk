# Part 1: Core Foundation Infrastructure - Architecture Documentation

**Created:** 2025-10-15 17:00:00  
**Package ID:** part1_phase3_code-preparator_Core-Foundation-Infrastructure_ARCHITECTURE.md  
**Status:** READY FOR CODING AGENTS

## Executive Summary

This architecture document provides the complete technical design for Part 1: Core Foundation Infrastructure. The architecture implements a **hierarchical multi-agent system (HMAS)** with TeamLeader orchestration at its core, designed for **enterprise-grade reliability**, **security-first operations**, and **developer-friendly integration**.

**Key Architectural Decisions:**
- **Hierarchical coordination** with TeamLeader as central orchestrator
- **WebSocket-based real-time communication** for agent coordination
- **Dynamic .md system prompt loading** with hot-reload capabilities
- **MCP server integration** with fallback mechanisms
- **OAuth2 + RBAC security framework** from day one
- **Structured concurrency patterns** using Python 3.11+ task groups

## System Architecture Overview

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    AI Agent Dev Team SDK                     │
│                      Part 1: Foundation                     │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    Security Framework                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │  OAuth2     │  │     RBAC    │  │   Audit Logging     │  │
│  │  Provider   │  │  Manager    │  │   & Monitoring      │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                               │
┌─────────────────────────────────────────────────────────────┐
│                    TeamLeader Agent                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ Rules       │  │  Task       │  │   Context           │  │
│  │ Engine      │  │ Delegation  │  │   Manager           │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                               │
┌─────────────────────────────────────────────────────────────┐
│                Communication Infrastructure                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ WebSocket   │  │  Message    │  │   Connection        │  │
│  │ Server      │  │  Router     │  │   Manager           │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                               │
┌─────────────────────────────────────────────────────────────┐
│                    Sub-Agent Layer                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ Research    │  │  CodeBase   │  │  FrontEnd/BackEnd   │  │
│  │ Agent       │  │ Analyzer    │  │    Coders           │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                               │
┌─────────────────────────────────────────────────────────────┐
│                   MCP Integration Layer                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ Perplexity  │  │   Serena    │  │   MCP               │  │
│  │ Server      │  │   Server    │  │   Client            │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack Configuration

**Core Framework Stack:**
```yaml
primary_framework:
  name: "Claude Agent SDK (Python)"
  version: ">=2.0.0"
  justification: "90.2% performance improvement in multi-agent coordination, rich tool ecosystem"

communication:
  protocol: "WebSocket (RFC 6455)"
  library: "websockets (Python) with permessage-deflate compression"
  features: ["Bidirectional", "Real-time", "Connection pooling", "Acknowledgments"]

async_runtime:
  runtime: "Python asyncio with structured concurrency"
  version: "Python 3.11+"
  patterns: ["Task groups", "Context managers", "Resource cleanup"]

configuration:
  manager: "Dynaconf"
  formats: ["YAML", "JSON", "ENV"]
  features: ["Environment-specific", "Hot reload", "Validation"]

mcp_integration:
  client: "Custom MCP client with FastMCP compatibility"
  servers: ["Perplexity", "Serena"]
  protocol: "JSON-RPC over stdio/HTTP"

security:
  authentication: "OAuth2 + OpenID Connect"
  authorization: "Role-Based Access Control (RBAC)"
  encryption: "TLS 1.3 with perfect forward secrecy"
```

**Supporting Infrastructure:**
```yaml
development_tools:
  package_manager: "UV (Ultra-fast Python package manager)"
  testing_framework: "pytest with async support"
  code_quality: ["black", "ruff", "mypy"]
  documentation: "Sphinx with auto-api generation"

monitoring:
  logging: "structlog with JSON formatting"
  metrics: "Prometheus client library"
  tracing: "OpenTelemetry integration"
  health_checks: "Custom health check endpoints"

containerization:
  runtime: "Docker with multi-stage builds"
  orchestration: "docker-compose for development"
  base_images: ["python:3.11-slim", "nginx:alpine"]
```

## Component Architecture

### 1. TeamLeader Agent Architecture

#### Core TeamLeader Implementation

```python
class TeamLeader:
    """
    Central orchestration agent with rules engine and delegation capabilities.
    Implements hierarchical coordination with validation gates and scope enforcement.
    """

    def __init__(self, config_path: str = "config/team_leader.yaml"):
        self.config = self._load_config(config_path)
        self.rules_engine = RulesEngine(self.config.rules)
        self.agent_registry = AgentRegistry()
        self.context_manager = ContextManager()
        self.security_manager = SecurityManager()
        self.mcp_client = MCPClient()

    async def initialize(self):
        """Initialize TeamLeader with all subsystems."""
        await self._load_system_prompts()
        await self._initialize_agents()
        await self._establish_mcp_connections()
        await self._start_monitoring()

    async def delegate_task(self, task_spec: TaskSpec) -> TaskResult:
        """
        Delegate task to appropriate sub-agent with proper context and validation.
        Implements the core delegation pattern with scope checking.
        """
        # 1. Validate task against scope boundaries
        if not self.rules_engine.validate_scope(task_spec):
            raise ScopeViolationError("Task exceeds approved scope boundaries")

        # 2. Load appropriate system prompt
        system_prompt = await self.context_manager.load_prompt(
            agent_type=task_spec.agent_type,
            task_type=task_spec.task_type
        )

        # 3. Select and prepare agent
        agent = await self.agent_registry.get_agent(task_spec.agent_type)
        context = await self.context_manager.prepare_context(task_spec)

        # 4. Execute task with monitoring
        async with self._task_monitor(task_spec) as monitor:
            result = await agent.execute(
                task=task_spec.task,
                system_prompt=system_prompt,
                context=context,
                monitor=monitor
            )

        # 5. Validate result and update context
        await self._validate_result(result, task_spec)
        await self.context_manager.update_context(result)

        return result
```

#### Rules Engine Architecture

```python
class RulesEngine:
    """
    Programmatic rules engine implementing the ten-phase development process
    with validation gates and scope enforcement.
    """

    def __init__(self, rules_config: Dict[str, Any]):
        self.rules = self._load_rules(rules_config)
        self.current_phase = "INITIALIZATION"
        self.phase_history = []

    def validate_scope(self, task_spec: TaskSpec) -> bool:
        """Validate task against current scope boundaries."""
        # Check phase-appropriate tasks
        allowed_tasks = self.rules["phases"][self.current_phase]["allowed_tasks"]
        if task_spec.task_type not in allowed_tasks:
            return False

        # Check complexity budget
        current_complexity = self._calculate_current_complexity()
        if current_complexity + task_spec.complexity > self.rules["complexity_budget"]:
            return False

        # Check agent availability
        if not self._agent_available(task_spec.agent_type):
            return False

        return True

    def can_progress_to_phase(self, target_phase: str) -> bool:
        """Check if progression to target phase is allowed."""
        current_requirements = self.rules["phases"][self.current_phase]["completion_criteria"]

        for requirement in current_requirements:
            if not self._check_requirement(requirement):
                return False

        return True
```

#### Context Management Architecture

```python
class ContextManager:
    """
    Manages system prompt loading, context preparation, and conversation history.
    Implements hot-reload capabilities and caching for optimal performance.
    """

    def __init__(self, prompts_dir: str = "system_prompts"):
        self.prompts_dir = Path(prompts_dir)
        self.prompt_cache = LRUCache(maxsize=1000)
        self.context_history = ContextHistory()
        self.watcher = self._setup_file_watcher()

    async def load_prompt(self, agent_type: str, task_type: str = None) -> str:
        """
        Load system prompt from .md file with caching and validation.
        Supports hot-reload for development efficiency.
        """
        prompt_file = self._get_prompt_file(agent_type, task_type)

        # Check cache first
        if prompt_file in self.prompt_cache:
            cached_content, checksum = self.prompt_cache[prompt_file]
            if self._validate_checksum(prompt_file, checksum):
                return cached_content

        # Load and validate file
        content = await self._read_and_validate_prompt(prompt_file)
        checksum = self._calculate_checksum(prompt_file)

        # Update cache
        self.prompt_cache[prompt_file] = (content, checksum)

        return content
```

### 2. Sub-Agent Architecture

#### Base Agent Implementation

```python
class BaseAgent:
    """
    Base class for all specialized sub-agents with Claude SDK integration.
    Provides common functionality for task execution and communication.
    """

    def __init__(self, agent_type: str, config: Dict[str, Any]):
        self.agent_type = agent_type
        self.config = config
        self.claude_client = self._initialize_claude_client()
        self.websocket_client = WebSocketClient()
        self.mcp_integrations = self._setup_mcp_integrations()

    async def execute(self, task: str, system_prompt: str, context: AgentContext,
                     monitor: TaskMonitor) -> TaskResult:
        """
        Execute task using Claude SDK with comprehensive error handling and monitoring.
        """
        try:
            # Start execution monitoring
            await monitor.start_execution(self.agent_type, task)

            # Prepare Claude SDK request
            messages = self._prepare_messages(task, system_prompt, context)

            # Execute via Claude SDK
            response = await self.claude_client.messages.create(
                model=self.config["claude_model"],
                max_tokens=self.config["max_tokens"],
                temperature=self.config["temperature"],
                system=system_prompt,
                messages=messages
            )

            # Process response
            result = await self._process_response(response, context)

            # Validate result quality
            await self._validate_result(result)

            # Report completion
            await monitor.complete_execution(result)

            return result

        except Exception as e:
            await monitor.handle_error(e)
            raise AgentExecutionError(f"Task execution failed: {e}")
```

#### Specialized Agent Architectures

**ResearchAgent Architecture:**
```python
class ResearchAgent(BaseAgent):
    """
    Specialized agent for research tasks with Perplexity MCP integration.
    Handles web research, knowledge synthesis, and competitive analysis.
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__("research", config)
        self.perplexity_client = self.mcp_integrations["perplexity"]

    async def execute_research_task(self, query: str, context: AgentContext) -> ResearchResult:
        """
        Execute comprehensive research using Perplexity MCP and internal capabilities.
        """
        # Use Perplexity MCP for enhanced research
        perplexity_result = await self.perplexity_client.research(query)

        # Synthesize with internal knowledge
        synthesis_prompt = self._build_synthesis_prompt(query, perplexity_result)

        # Execute synthesis via Claude SDK
        synthesis_result = await self.execute(
            task=synthesis_prompt,
            system_prompt=await self.load_prompt("research_synthesis"),
            context=context,
            monitor=self.monitor
        )

        return ResearchResult(
            original_query=query,
            perplexity_data=perplexity_result,
            synthesis=synthesis_result,
            sources=self._extract_sources(perplexity_result, synthesis_result)
        )
```

**CodeBaseAnalyzer Architecture:**
```python
class CodeBaseAnalyzer(BaseAgent):
    """
    Specialized agent for code analysis with Serena MCP integration.
    Handles code review, architecture analysis, and dependency mapping.
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__("codebase_analyzer", config)
        self.serena_client = self.mcp_integrations["serena"]

    async def analyze_codebase(self, repository_path: str,
                              analysis_type: str) -> CodeAnalysisResult:
        """
        Analyze codebase using Serena MCP and internal analysis capabilities.
        """
        # Use Serena MCP for code intelligence
        serena_analysis = await self.serena_client.analyze_code(
            repository_path, analysis_type
        )

        # Perform additional analysis
        detailed_analysis = await self._perform_detailed_analysis(
            repository_path, serena_analysis
        )

        return CodeAnalysisResult(
            repository_path=repository_path,
            analysis_type=analysis_type,
            serena_data=serena_analysis,
            detailed_analysis=detailed_analysis,
            recommendations=self._generate_recommendations(detailed_analysis)
        )
```

### 3. Communication Infrastructure Architecture

#### WebSocket Server Architecture

```python
class AgentCommunicationHub:
    """
    WebSocket-based communication hub for real-time agent coordination.
    Implements pub/sub patterns with acknowledgment mechanisms.
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.connections: Dict[str, WebSocket] = {}
        self.message_queue = asyncio.Queue()
        self.subscription_manager = SubscriptionManager()
        self.security_manager = SecurityManager()

    async def start_server(self):
        """Start WebSocket server with authentication and routing."""
        async def handle_connection(websocket, path):
            # Authenticate connection
            agent_id = await self._authenticate_connection(websocket)
            if not agent_id:
                await websocket.close(code=4001, reason="Authentication failed")
                return

            # Register connection
            self.connections[agent_id] = websocket

            try:
                async for message in websocket:
                    await self._route_message(agent_id, message)
            except websockets.exceptions.ConnectionClosed:
                self._cleanup_connection(agent_id)

        # Start server
        self.server = await websockets.serve(
            handle_connection,
            self.config["host"],
            self.config["port"],
            extra_headers={"Server": "AI-Agent-SDK/1.0"}
        )
```

#### Message Protocol Architecture

```python
@dataclass
class AgentMessage:
    """Standardized message format for agent communication."""
    message_id: str
    sender: str
    recipient: str
    message_type: str
    timestamp: datetime
    payload: Dict[str, Any]
    correlation_id: str = None
    requires_ack: bool = True
    priority: int = 5  # 1-10, where 10 is highest priority

    def to_dict(self) -> Dict[str, Any]:
        return {
            "message_id": self.message_id,
            "sender": self.sender,
            "recipient": self.recipient,
            "type": self.message_type,
            "timestamp": self.timestamp.isoformat(),
            "payload": self.payload,
            "correlation_id": self.correlation_id,
            "requires_ack": self.requires_ack,
            "priority": self.priority
        }
```

### 4. MCP Integration Architecture

#### Universal MCP Client Architecture

```python
class MCPClient:
    """
    Universal MCP client with support for multiple server types.
    Implements standardized JSON-RPC communication with error handling.
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.servers: Dict[str, MCPServerConnection] = {}
        self.health_checker = HealthChecker()

    async def initialize_servers(self):
        """Initialize all configured MCP servers."""
        for server_name, server_config in self.config["servers"].items():
            try:
                connection = await self._create_server_connection(
                    server_name, server_config
                )
                self.servers[server_name] = connection

                # Start health monitoring
                await self.health_checker.start_monitoring(
                    server_name, connection
                )

            except Exception as e:
                logger.error(f"Failed to initialize MCP server {server_name}: {e}")

    async def call(self, server_name: str, method: str, params: Dict[str, Any]) -> Any:
        """
        Call method on MCP server with automatic retry and fallback.
        """
        server = self.servers.get(server_name)
        if not server:
            raise MCPServerError(f"Server {server_name} not available")

        # Check server health
        if not await self.health_checker.is_healthy(server_name):
            return await self._handle_server_failure(server_name, method, params)

        try:
            # Execute RPC call with timeout
            result = await asyncio.wait_for(
                server.call(method, params),
                timeout=self.config["timeout"]
            )

            # Validate response
            if not self._validate_response(result):
                raise MCPResponseError("Invalid response format")

            return result

        except asyncio.TimeoutError:
            logger.error(f"Timeout calling {method} on {server_name}")
            return await self._handle_server_failure(server_name, method, params)
```

#### Server-Specific Integration Architectures

**Perplexity MCP Integration:**
```python
class PerplexityMCPServer(MCPServerConnection):
    """
    Perplexity MCP server integration for enhanced research capabilities.
    Supports multiple complexity levels and specialized research modes.
    """

    async def research(self, query: str, complexity_level: str = "medium",
                      research_mode: str = "comprehensive") -> ResearchResult:
        """
        Execute research query with specified complexity and mode.
        """
        params = {
            "query": query,
            "complexity_level": complexity_level,
            "research_mode": research_mode,
            "max_sources": self._get_max_sources(complexity_level),
            "include_analysis": True
        }

        result = await self.call("research", params)

        return ResearchResult(
            query=query,
            sources=result["sources"],
            analysis=result["analysis"],
            confidence_score=result["confidence_score"],
            completion_time=result["completion_time"]
        )
```

**Serena MCP Integration:**
```python
class SerenaMCPServer(MCPServerConnection):
    """
    Serena MCP server integration for code analysis and generation.
    Provides intelligent code review and enhancement suggestions.
    """

    async def analyze_code(self, repository_path: str,
                          analysis_type: str = "comprehensive") -> CodeAnalysis:
        """
        Analyze code repository with specified analysis type.
        """
        params = {
            "repository_path": repository_path,
            "analysis_type": analysis_type,
            "include_suggestions": True,
            "check_security": True
        }

        result = await self.call("analyze_code", params)

        return CodeAnalysis(
            repository_path=repository_path,
            analysis_type=analysis_type,
            findings=result["findings"],
            suggestions=result["suggestions"],
            security_issues=result["security_issues"],
            metrics=result["metrics"]
        )
```

### 5. Security Framework Architecture

#### Authentication and Authorization Architecture

```python
class SecurityManager:
    """
    Comprehensive security manager implementing OAuth2 authentication,
    RBAC authorization, and audit logging.
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.oauth_provider = OAuth2Provider(config["oauth"])
        self.rbac_manager = RBACManager(config["rbac"])
        self.audit_logger = AuditLogger(config["audit"])
        self.token_manager = TokenManager()

    async def authenticate_agent(self, token: str) -> AgentIdentity:
        """
        Authenticate agent using OAuth2 token and return identity.
        """
        try:
            # Validate OAuth2 token
            token_info = await self.oauth_provider.validate_token(token)

            # Extract agent identity
            agent_id = token_info["sub"]
            permissions = await self.rbac_manager.get_permissions(agent_id)

            # Create agent identity
            identity = AgentIdentity(
                agent_id=agent_id,
                permissions=permissions,
                token_info=token_info,
                authenticated_at=datetime.utcnow()
            )

            # Log authentication event
            await self.audit_logger.log_authentication_success(identity)

            return identity

        except Exception as e:
            await self.audit_logger.log_authentication_failure(token, str(e))
            raise AuthenticationError(f"Authentication failed: {e}")
```

#### RBAC Implementation Architecture

```python
class RBACManager:
    """
    Role-Based Access Control manager with fine-grained permissions.
    Supports hierarchical roles and resource-specific permissions.
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.role_definitions = self._load_role_definitions()
        self.permission_cache = LRUCache(maxsize=10000)

    async def get_permissions(self, agent_id: str) -> Set[str]:
        """
        Get all permissions for agent based on roles and assignments.
        """
        # Check cache first
        if agent_id in self.permission_cache:
            return self.permission_cache[agent_id]

        # Get agent roles
        roles = await self._get_agent_roles(agent_id)

        # Collect permissions from all roles
        permissions = set()
        for role in roles:
            role_permissions = self.role_definitions[role]["permissions"]
            permissions.update(role_permissions)

        # Add any direct permissions
        direct_permissions = await self._get_direct_permissions(agent_id)
        permissions.update(direct_permissions)

        # Cache result
        self.permission_cache[agent_id] = permissions

        return permissions
```

## Data Architecture

### Data Models and Entity Relationships

#### Core Data Models

```python
@dataclass
class TaskSpec:
    """Task specification for agent execution."""
    task_id: str
    agent_type: str
    task_type: str
    task: str
    complexity: int
    priority: int
    project_id: str
    context_hash: str = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TaskResult:
    """Result from agent task execution."""
    task_id: str
    agent_id: str
    status: str
    content: str
    execution_time: float
    confidence_score: float
    sources: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AgentContext:
    """Context provided to agents for task execution."""
    system_prompt: str
    history: List[Dict[str, Any]]
    mcp_context: Dict[str, Any]
    task_spec: TaskSpec
    metadata: Dict[str, Any]
```

#### Database Schema Design

```sql
-- Agents table
CREATE TABLE agents (
    agent_id VARCHAR(255) PRIMARY KEY,
    agent_type VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL,
    capabilities JSONB,
    last_heartbeat TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tasks table
CREATE TABLE tasks (
    task_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_type VARCHAR(100) NOT NULL,
    task_type VARCHAR(100) NOT NULL,
    task_content TEXT NOT NULL,
    complexity INTEGER NOT NULL,
    priority INTEGER DEFAULT 5,
    status VARCHAR(50) DEFAULT 'pending',
    project_id VARCHAR(255),
    context_hash VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Task results table
CREATE TABLE task_results (
    result_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID REFERENCES tasks(task_id),
    agent_id VARCHAR(255) REFERENCES agents(agent_id),
    status VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    execution_time FLOAT,
    confidence_score FLOAT,
    sources JSONB,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Audit log table
CREATE TABLE audit_logs (
    log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id VARCHAR(255),
    event_type VARCHAR(100) NOT NULL,
    resource_type VARCHAR(100),
    resource_id VARCHAR(255),
    action VARCHAR(100),
    outcome VARCHAR(50),
    details JSONB,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Data Flow Architecture

#### Task Execution Flow

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Client    │───▶│ TeamLeader  │───▶│ RulesEngine │───▶│ Validation  │
│   Request   │    │   Router    │    │   Check     │    │   Gate      │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                           │                   │                   │
                           ▼                   ▼                   ▼
                   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
                   │  Context    │    │   Agent     │    │   Result    │
                   │ Preparation │    │ Selection   │    │ Collection  │
                   └─────────────┘    └─────────────┘    └─────────────┘
                           │                   │                   │
                           ▼                   ▼                   ▼
                   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
                   │  System     │    │ WebSocket   │    │   Audit     │
                   │  Prompt     │    │ Execution   │    │   Logging   │
                   │  Loading    │    │ Monitoring  │    │             │
                   └─────────────┘    └─────────────┘    └─────────────┘
```

#### Message Flow Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Team      │    │   Message   │    │   Message   │    │   Target    │
│   Leader    │───▶│   Queue     │───▶│   Router    │───▶│   Agent     │
│  Request    │    │             │    │             │    │             │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                           │                   │                   │
                           ▼                   ▼                   ▼
                   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
                   │ Priority    │    │  Security   │    │   Agent     │
                   │ Management  │    │ Validation  │    │ Execution   │
                   └─────────────┘    └─────────────┘    └─────────────┘
                           │                   │                   │
                           ▼                   ▼                   ▼
                   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
                   │   Message   │    │   Response  │    │   Status    │
                   │ Delivery    │    │   Routing   │    │ Reporting   │
                   │ Tracking    │    │             │    │             │
                   └─────────────┘    └─────────────┘    └─────────────┘
```

## Integration Patterns

### MCP Integration Patterns

#### Circuit Breaker Pattern for MCP Servers

```python
class MCPCircuitBreaker:
    """
    Circuit breaker pattern for MCP server reliability.
    Prevents cascade failures and provides fallback mechanisms.
    """

    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 30):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    async def call(self, server_func, *args, **kwargs):
        """Execute server function with circuit breaker protection."""
        if self.state == "OPEN":
            if self._should_attempt_reset():
                self.state = "HALF_OPEN"
            else:
                raise MCPServerError("Circuit breaker is OPEN")

        try:
            result = await server_func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e

    def _should_attempt_reset(self) -> bool:
        """Check if circuit breaker should attempt reset."""
        return (time.time() - self.last_failure_time) > self.recovery_timeout
```

#### Retry Pattern with Exponential Backoff

```python
class MCPRetryPolicy:
    """
    Retry policy with exponential backoff for MCP server calls.
    Handles transient failures and improves reliability.
    """

    def __init__(self, max_attempts: int = 3, base_delay: float = 1.0, max_delay: float = 30.0):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay

    async def execute_with_retry(self, func, *args, **kwargs):
        """Execute function with retry policy."""
        for attempt in range(self.max_attempts):
            try:
                return await func(*args, **kwargs)
            except (ConnectionError, TimeoutError) as e:
                if attempt == self.max_attempts - 1:
                    raise e

                delay = min(self.base_delay * (2 ** attempt), self.max_delay)
                await asyncio.sleep(delay)
```

### Security Integration Patterns

#### OAuth2 Token Management

```python
class TokenManager:
    """
    OAuth2 token management with automatic refresh and caching.
    Handles token lifecycle and security.
    """

    def __init__(self):
        self.token_cache = {}
        self.refresh_callbacks = {}

    async def get_valid_token(self, provider: str, client_id: str, 
                             client_secret: str) -> str:
        """Get valid OAuth2 token with automatic refresh."""
        cache_key = f"{provider}:{client_id}"
        
        if cache_key in self.token_cache:
            token_data = self.token_cache[cache_key]
            if not self._token_expired(token_data):
                return token_data["access_token"]

        # Obtain new token
        token_data = await self._obtain_token(provider, client_id, client_secret)
        self.token_cache[cache_key] = token_data

        return token_data["access_token"]

    def _token_expired(self, token_data: Dict[str, Any]) -> bool:
        """Check if token is expired or about to expire."""
        expires_at = token_data.get("expires_at")
        if not expires_at:
            return True
        
        # Refresh 5 minutes before expiration
        return time.time() > (expires_at - 300)
```

#### Permission Caching Pattern

```python
class PermissionCache:
    """
    Permission caching with invalidation for RBAC performance.
    Improves authorization performance while maintaining security.
    """

    def __init__(self, ttl: int = 300):
        self.cache = {}
        self.ttl = ttl

    async def get_permissions(self, agent_id: str) -> Optional[Set[str]]:
        """Get cached permissions for agent."""
        cache_entry = self.cache.get(agent_id)
        if not cache_entry:
            return None

        if self._cache_expired(cache_entry):
            del self.cache[agent_id]
            return None

        return cache_entry["permissions"]

    async def set_permissions(self, agent_id: str, permissions: Set[str]):
        """Cache permissions for agent."""
        self.cache[agent_id] = {
            "permissions": permissions,
            "cached_at": time.time()
        }

    def invalidate_permissions(self, agent_id: str):
        """Invalidate cached permissions for agent."""
        self.cache.pop(agent_id, None)
```

## Performance Optimization Patterns

### Connection Pooling

```python
class WebSocketConnectionPool:
    """
    Connection pool for WebSocket connections to improve performance.
    Manages connection lifecycle and resource utilization.
    """

    def __init__(self, max_connections: int = 100):
        self.max_connections = max_connections
        self.available_connections = asyncio.Queue()
        self.active_connections = set()
        self.connection_count = 0

    async def get_connection(self, endpoint: str) -> WebSocket:
        """Get WebSocket connection from pool."""
        try:
            connection = self.available_connections.get_nowait()
            if self._connection_valid(connection):
                self.active_connections.add(connection)
                return connection
        except asyncio.QueueEmpty:
            pass

        # Create new connection
        connection = await self._create_connection(endpoint)
        self.active_connections.add(connection)
        self.connection_count += 1

        return connection

    async def return_connection(self, connection: WebSocket):
        """Return connection to pool."""
        if connection in self.active_connections:
            self.active_connections.remove(connection)
            if self._connection_valid(connection):
                await self.available_connections.put(connection)
            else:
                await connection.close()
                self.connection_count -= 1
```

### Context Caching

```python
class ContextCache:
    """
    Context caching with LRU eviction for performance optimization.
    Reduces context loading overhead for repeated tasks.
    """

    def __init__(self, max_size: int = 1000):
        self.cache = LRUCache(maxsize=max_size)
        self.hit_count = 0
        self.miss_count = 0

    async def get_cached_context(self, context_hash: str) -> Optional[AgentContext]:
        """Get cached context if available."""
        context = self.cache.get(context_hash)
        if context:
            self.hit_count += 1
            return context
        
        self.miss_count += 1
        return None

    async def cache_context(self, context_hash: str, context: AgentContext):
        """Cache context for future use."""
        self.cache[context_hash] = context

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics."""
        total_requests = self.hit_count + self.miss_count
        hit_rate = self.hit_count / total_requests if total_requests > 0 else 0
        
        return {
            "hit_count": self.hit_count,
            "miss_count": self.miss_count,
            "hit_rate": hit_rate,
            "cache_size": len(self.cache)
        }
```

## Deployment Architecture

### Container Architecture

```dockerfile
# Dockerfile for TeamLeader service
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install UV for fast package management
RUN pip install uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --dev

# Copy source code
COPY src/ ./src/
COPY config/ ./config/
COPY system_prompts/ ./system_prompts/

# Create non-root user
RUN useradd -m -u 1000 agent && chown -R agent:agent /app
USER agent

# Expose ports
EXPOSE 8000 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command
CMD ["uv", "run", "python", "-m", "src.main"]
```

### Development Environment Architecture

```yaml
# docker-compose.dev.yml
version: '3.8'

services:
  team-leader:
    build:
      context: .
      dockerfile: Dockerfile
    volumes:
      - ./src:/app/src
      - ./config:/app/config
      - ./system_prompts:/app/system_prompts
      - ./logs:/app/logs
    environment:
      - PYTHONPATH=/app
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - PERPLEXITY_API_KEY=${PERPLEXITY_API_KEY}
      - SERENA_API_KEY=${SERENA_API_KEY}
      - LOG_LEVEL=DEBUG
      - ENVIRONMENT=development
    ports:
      - "8000:8000"  # REST API
      - "8080:8080"  # WebSocket server
    depends_on:
      - redis
      - postgres
    command: uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=ai_agent_sdk
      - POSTGRES_USER=developer
      - POSTGRES_PASSWORD=dev_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init_db.sql:/docker-entrypoint-initdb.d/init.sql

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana

volumes:
  redis_data:
  postgres_data:
  grafana_data:
```

## Monitoring and Observability Architecture

### Metrics Collection

```python
class MetricsCollector:
    """
    Comprehensive metrics collection for system monitoring.
    Tracks performance, reliability, and business metrics.
    """

    def __init__(self):
        self.prometheus_client = PrometheusClient()
        self.metrics = {
            "agent_executions_total": Counter(
                "agent_executions_total",
                "Total number of agent executions",
                ["agent_type", "status"]
            ),
            "agent_execution_duration": Histogram(
                "agent_execution_duration_seconds",
                "Agent execution duration in seconds",
                ["agent_type", "task_type"]
            ),
            "websocket_connections_active": Gauge(
                "websocket_connections_active",
                "Number of active WebSocket connections"
            ),
            "mcp_server_requests": Counter(
                "mcp_server_requests_total",
                "Total MCP server requests",
                ["server_name", "method", "status"]
            ),
            "system_prompt_load_time": Histogram(
                "system_prompt_load_duration_seconds",
                "System prompt loading duration"
            )
        }

    def record_agent_execution(self, agent_type: str, status: str, 
                             duration: float, task_type: str):
        """Record agent execution metrics."""
        self.metrics["agent_executions_total"].labels(
            agent_type=agent_type, status=status
        ).inc()
        
        self.metrics["agent_execution_duration"].labels(
            agent_type=agent_type, task_type=task_type
        ).observe(duration)

    def record_websocket_connection(self, active_connections: int):
        """Record WebSocket connection metrics."""
        self.metrics["websocket_connections_active"].set(active_connections)

    def record_mcp_request(self, server_name: str, method: str, 
                          status: str):
        """Record MCP server request metrics."""
        self.metrics["mcp_server_requests"].labels(
            server_name=server_name, method=method, status=status
        ).inc()
```

### Health Check Architecture

```python
class HealthCheckRegistry:
    """
    Health check registry for comprehensive system monitoring.
    Tracks component health and system status.
    """

    def __init__(self):
        self.checks = {}
        self.results = {}

    def register_check(self, name: str, check_func: Callable, 
                      timeout: int = 30):
        """Register health check function."""
        self.checks[name] = {
            "function": check_func,
            "timeout": timeout
        }

    async def run_all_checks(self) -> Dict[str, Any]:
        """Run all registered health checks."""
        results = {}
        
        for name, check_config in self.checks.items():
            try:
                start_time = time.time()
                result = await asyncio.wait_for(
                    check_config["function"](),
                    timeout=check_config["timeout"]
                )
                duration = time.time() - start_time
                
                results[name] = {
                    "status": "healthy" if result else "unhealthy",
                    "duration": duration,
                    "timestamp": datetime.utcnow().isoformat(),
                    "details": result if isinstance(result, dict) else {}
                }
            except Exception as e:
                results[name] = {
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }

        self.results = results
        return results

    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health status."""
        if not self.results:
            return {"status": "unknown", "message": "No health checks run"}

        healthy_count = sum(1 for r in self.results.values() 
                          if r["status"] == "healthy")
        total_count = len(self.results)

        if healthy_count == total_count:
            overall_status = "healthy"
        elif healthy_count > 0:
            overall_status = "degraded"
        else:
            overall_status = "unhealthy"

        return {
            "status": overall_status,
            "healthy_checks": healthy_count,
            "total_checks": total_count,
            "components": self.results
        }
```

---

## Architecture Decision Records

### ADR-001: Hierarchical Multi-Agent System

**Status:** Accepted  
**Date:** 2025-10-15  
**Decision:** Implement hierarchical multi-agent system with TeamLeader orchestration

**Rationale:**
- Proven pattern with 90.2% performance improvement in coordination
- Simplifies complexity through centralized planning with decentralized execution
- Enables clear scope boundaries and validation gates
- Supports enterprise security and compliance requirements

**Alternatives Considered:**
- Flat peer-to-peer coordination (rejected for complexity)
- Federated agent system (deferred to Part 2)
- Event-driven architecture (partially adopted)

### ADR-002: WebSocket-Based Communication

**Status:** Accepted  
**Date:** 2025-10-15  
**Decision:** Use WebSocket (RFC 6455) for real-time agent communication

**Rationale:**
- Low latency bidirectional communication (<100ms target)
- Mature technology with extensive library support
- Supports real-time coordination requirements
- Efficient message handling with connection pooling

**Alternatives Considered:**
- HTTP/REST API (rejected for latency)
- Message queues (used for async communication)
- gRPC (considered for future performance optimization)

### ADR-003: Dynamic System Prompt Loading

**Status:** Accepted  
**Date:** 2025-10-15  
**Decision:** Implement dynamic .md system prompt loading with hot-reload

**Rationale:**
- Enables easy updates without code changes
- Supports rapid iteration and testing
- Improves developer experience
- Facilitates customization and extensibility

**Alternatives Considered:**
- Hard-coded prompts (rejected for inflexibility)
- Database storage (rejected for complexity)
- Configuration file loading (used for other configuration)

### ADR-004: Security-First Architecture

**Status:** Accepted  
**Date:** 2025-10-15  
**Decision:** Implement OAuth2 + RBAC security from day one

**Rationale:**
- Enterprise requirements demand robust security
- Early implementation prevents security debt
- Enables enterprise adoption and compliance
- Reduces retrofitting complexity

**Alternatives Considered:**
- API key authentication (insufficient for enterprise)
- JWT-only authentication (limited to token-based)
- Custom authentication (rejected for maintenance overhead)

---

## Document Status

**Status:** READY FOR CODING AGENTS  
**Validation:** All architecture decisions reviewed and approved  
**Completeness:** 100% - All components and patterns defined  
**Traceability:** All architecture decisions traceable to requirements  

**Next Steps:** Coding agents should use this architecture documentation in conjunction with the requirements specification and implementation guidelines.
