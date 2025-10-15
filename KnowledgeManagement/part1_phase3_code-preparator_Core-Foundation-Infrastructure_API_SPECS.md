# Part 1: Core Foundation Infrastructure - API Specifications

**Created:** 2025-10-15 17:00:00  
**Package ID:** part1_phase3_code-preparator_Core-Foundation-Infrastructure_API_SPECS.md  
**Status:** READY FOR CODING AGENTS

## Executive Summary

This document provides comprehensive API specifications for Part 1: Core Foundation Infrastructure. The specifications cover REST APIs, WebSocket communication protocols, MCP server integration, and internal service interfaces required for the AI Agent Dev Team SDK.

**API Categories:**
- **REST APIs**: TeamLeader management, task orchestration, system administration
- **WebSocket APIs**: Real-time agent communication, status updates, message routing
- **MCP APIs**: External service integration (Perplexity, Serena)
- **Internal APIs**: Service-to-service communication within the SDK

## REST API Specifications

### Base Configuration

```yaml
base_url: "http://localhost:8000/api/v1"
api_version: "1.0.0"
content_type: "application/json"
authentication: "Bearer Token (OAuth2)"
rate_limiting: "1000 requests per hour per user"
```

### 1. TeamLeader Management APIs

#### 1.1 Initialize TeamLeader

**Endpoint:** `POST /team-leader/initialize`  
**Description:** Initialize TeamLeader with all subsystems  
**Authentication:** Required  
**Rate Limit:** 10 requests per minute

```yaml
request:
  method: "POST"
  path: "/team-leader/initialize"
  headers:
    Authorization: "Bearer {access_token}"
    Content-Type: "application/json"
  body:
    config_path: "config/team_leader.yaml"  # optional
    force_restart: false                    # optional

response:
  status_code: 200
  body:
    status: "success"
    team_leader_id: "tl_123456789"
    initialization_time: "2025-10-15T17:00:00Z"
    subsystems:
      rules_engine: "operational"
      agent_registry: "operational"
      context_manager: "operational"
      security_manager: "operational"
      mcp_client: "operational"
    version: "1.0.0"

error_responses:
  400:
    description: "Invalid configuration"
    body:
      error: "INVALID_CONFIGURATION"
      message: "TeamLeader configuration is invalid"
      details:
        missing_fields: ["rules_engine_config"]
  401:
    description: "Authentication required"
    body:
      error: "UNAUTHORIZED"
      message: "Valid authentication token required"
  500:
    description: "Initialization failed"
    body:
      error: "INITIALIZATION_FAILED"
      message: "TeamLeader failed to initialize"
      details:
        subsystem: "mcp_client"
        error_code: "CONNECTION_REFUSED"
```

#### 1.2 Get TeamLeader Status

**Endpoint:** `GET /team-leader/{team_leader_id}/status`  
**Description:** Get current status and health of TeamLeader  
**Authentication:** Required  
**Rate Limit:** 100 requests per minute

```yaml
request:
  method: "GET"
  path: "/team-leader/{team_leader_id}/status"
  headers:
    Authorization: "Bearer {access_token}"
  parameters:
    path:
      team_leader_id: string  # TeamLeader instance ID

response:
  status_code: 200
  body:
    team_leader_id: "tl_123456789"
    status: "operational"
    uptime: 86400  # seconds
    current_phase: "RESEARCH"
    phase_progress: 0.6  # 60% complete
    active_agents: 4
    active_tasks: 3
    system_health:
      overall: "healthy"
      components:
        rules_engine: "healthy"
        agent_registry: "healthy"
        context_manager: "healthy"
        security_manager: "healthy"
        mcp_client: "healthy"
    performance_metrics:
      average_response_time: 0.25  # seconds
      task_success_rate: 0.98
      memory_usage: 1.2  # GB
      cpu_usage: 0.15  # 15%

error_responses:
  404:
    description: "TeamLeader not found"
    body:
      error: "TEAM_LEADER_NOT_FOUND"
      message: "TeamLeader with specified ID not found"
  503:
    description: "TeamLeader unavailable"
    body:
      error: "TEAM_LEADER_UNAVAILABLE"
      message: "TeamLeader is currently unavailable"
```

#### 1.3 Update TeamLeader Configuration

**Endpoint:** `PUT /team-leader/{team_leader_id}/config`  
**Description:** Update TeamLeader configuration  
**Authentication:** Required  
**Rate Limit:** 5 requests per minute

```yaml
request:
  method: "PUT"
  path: "/team-leader/{team_leader_id}/config"
  headers:
    Authorization: "Bearer {access_token}"
    Content-Type: "application/json"
  body:
    rules_engine:
      complexity_budget: 25
      phase_timeout: 3600  # seconds
    agent_registry:
      health_check_interval: 30  # seconds
    context_manager:
      prompt_cache_size: 1000
      cache_ttl: 300  # seconds
    mcp_client:
      timeout: 5  # seconds
      retry_attempts: 3

response:
  status_code: 200
  body:
    status: "success"
    updated_fields: ["rules_engine", "context_manager"]
    applied_at: "2025-10-15T17:00:00Z"
    requires_restart: false

error_responses:
  400:
    description: "Invalid configuration"
    body:
      error: "INVALID_CONFIGURATION"
      message: "Configuration validation failed"
      details:
        field: "rules_engine.complexity_budget"
        issue: "Value must be between 1 and 100"
  403:
    description: "Insufficient permissions"
    body:
      error: "INSUFFICIENT_PERMISSIONS"
      message: "User does not have configuration update permissions"
```

### 2. Task Management APIs

#### 2.1 Create and Delegate Task

**Endpoint:** `POST /tasks`  
**Description:** Create new task and delegate to appropriate agent  
**Authentication:** Required  
**Rate Limit:** 100 requests per minute

```yaml
request:
  method: "POST"
  path: "/tasks"
  headers:
    Authorization: "Bearer {access_token}"
    Content-Type: "application/json"
  body:
    agent_type: "research"  # research, codebase_analyzer, frontend, backend
    task_type: "market_analysis"
    task: "Analyze current AI agent coordination market trends"
    complexity: 5  # 1-10 scale
    priority: 7  # 1-10 scale, 10 highest
    project_id: "proj_123456789"
    metadata:
      deadline: "2025-10-20T17:00:00Z"
      requirements: ["competitive_analysis", "market_size"]
      sources_preference: ["industry_reports", "academic_papers"]

response:
  status_code: 201
  body:
    task_id: "task_123456789"
    status: "delegated"
    agent_id: "research_agent_001"
    team_leader_id: "tl_123456789"
    created_at: "2025-10-15T17:00:00Z"
    estimated_completion: "2025-10-15T17:05:00Z"
    delegation_details:
      selected_agent: "research_agent_001"
      selection_reason: "Specialized in market analysis tasks"
      context_hash: "ctx_abc123"
      system_prompt_loaded: true

error_responses:
  400:
    description: "Invalid task specification"
    body:
      error: "INVALID_TASK_SPECIFICATION"
      message: "Task specification is invalid"
      details:
        field: "complexity"
        issue: "Value must be between 1 and 10"
  403:
    description: "Scope violation"
    body:
      error: "SCOPE_VIOLATION"
      message: "Task exceeds approved scope boundaries"
      details:
        current_phase: "RESEARCH"
        allowed_task_types: ["research", "analysis"]
        requested_task_type: "development"
  503:
    description: "Agent unavailable"
    body:
      error: "AGENT_UNAVAILABLE"
      message: "No suitable agent available for task"
      details:
        requested_agent_type: "research"
        available_agents: []
        retry_after: 30  # seconds
```

#### 2.2 Get Task Status

**Endpoint:** `GET /tasks/{task_id}`  
**Description:** Get current status and progress of a task  
**Authentication:** Required  
**Rate Limit:** 200 requests per minute

```yaml
request:
  method: "GET"
  path: "/tasks/{task_id}"
  headers:
    Authorization: "Bearer {access_token}"
  parameters:
    path:
      task_id: string  # Task ID

response:
  status_code: 200
  body:
    task_id: "task_123456789"
    status: "in_progress"  # pending, delegated, in_progress, completed, failed
    agent_id: "research_agent_001"
    progress: 0.65  # 65% complete
    created_at: "2025-10-15T17:00:00Z"
    started_at: "2025-10-15T17:00:30Z"
    estimated_completion: "2025-10-15T17:05:00Z"
    execution_metrics:
      execution_time: 45  # seconds so far
      api_calls_made: 12
      tokens_used: 1500
      mcp_calls: 3
    current_activity:
      activity: "synthesizing_research_findings"
      step: 3
      total_steps: 5
      description: "Analyzing and synthesizing market research data"

error_responses:
  404:
    description: "Task not found"
    body:
      error: "TASK_NOT_FOUND"
      message: "Task with specified ID not found"
  403:
    description: "Access denied"
    body:
      error: "ACCESS_DENIED"
      message: "User does not have permission to access this task"
```

#### 2.3 Get Task Result

**Endpoint:** `GET /tasks/{task_id}/result`  
**Description:** Get final result of completed task  
**Authentication:** Required  
**Rate Limit:** 100 requests per minute

```yaml
request:
  method: "GET"
  path: "/tasks/{task_id}/result"
  headers:
    Authorization: "Bearer {access_token}"
  parameters:
    path:
      task_id: string  # Task ID
    query:
      format: "json"  # json, markdown, raw

response:
  status_code: 200
  body:
    task_id: "task_123456789"
    status: "completed"
    agent_id: "research_agent_001"
    completed_at: "2025-10-15T17:04:45Z"
    execution_time: 285  # seconds
    confidence_score: 0.87  # 87% confidence
    result:
      title: "AI Agent Coordination Market Analysis"
      summary: "The AI agent coordination market is experiencing rapid growth..."
      content: "Full detailed analysis content..."
      key_findings:
        - "Market size: $5.25B in 2024, growing to $52.62B by 2030"
        - "CAGR: 51.3% with enterprise adoption reaching 80% by 2026"
        - "Key players include CrewAI, LangGraph, AutoGen, and AWS Agent Squad"
      sources:
        - title: "Enterprise AI Adoption Survey 2024"
          url: "https://example.com/survey"
          credibility: 0.95
        - title: "AI Agent Market Analysis Report"
          url: "https://example.com/report"
          credibility: 0.89
      metadata:
        word_count: 1250
        sources_count: 8
        mcp_servers_used: ["perplexity"]
        model_used: "claude-3-sonnet-20241022"

error_responses:
  404:
    description: "Task not found"
    body:
      error: "TASK_NOT_FOUND"
      message: "Task with specified ID not found"
  425:
    description: "Task not completed"
    body:
      error: "TASK_NOT_COMPLETED"
      message: "Task has not completed yet"
      details:
        current_status: "in_progress"
        estimated_completion: "2025-10-15T17:05:00Z"
```

#### 2.4 List Tasks

**Endpoint:** `GET /tasks`  
**Description:** List tasks with filtering and pagination  
**Authentication:** Required  
**Rate Limit:** 100 requests per minute

```yaml
request:
  method: "GET"
  path: "/tasks"
  headers:
    Authorization: "Bearer {access_token}"
  parameters:
    query:
      status: "in_progress"  # optional: pending, delegated, in_progress, completed, failed
      agent_type: "research"  # optional: research, codebase_analyzer, frontend, backend
      project_id: "proj_123456789"  # optional
      limit: 20  # optional, default 20, max 100
      offset: 0  # optional, default 0
      sort_by: "created_at"  # optional: created_at, updated_at, priority, complexity
      sort_order: "desc"  # optional: asc, desc

response:
  status_code: 200
  body:
    tasks:
      - task_id: "task_123456789"
        status: "in_progress"
        agent_type: "research"
        task_type: "market_analysis"
        task: "Analyze current AI agent coordination market trends"
        complexity: 5
        priority: 7
        project_id: "proj_123456789"
        created_at: "2025-10-15T17:00:00Z"
        updated_at: "2025-10-15T17:03:15Z"
        progress: 0.65
        estimated_completion: "2025-10-15T17:05:00Z"
      - task_id: "task_123456790"
        status: "completed"
        agent_type: "codebase_analyzer"
        task_type: "security_analysis"
        task: "Perform security analysis on repository"
        complexity: 7
        priority: 8
        project_id: "proj_123456789"
        created_at: "2025-10-15T16:45:00Z"
        completed_at: "2025-10-15T16:52:30Z"
        progress: 1.0
    pagination:
      total_count: 45
      limit: 20
      offset: 0
      has_next: true
      has_prev: false
```

### 3. Agent Management APIs

#### 3.1 List Available Agents

**Endpoint:** `GET /agents`  
**Description:** List all available agents and their capabilities  
**Authentication:** Required  
**Rate Limit:** 50 requests per minute

```yaml
request:
  method: "GET"
  path: "/agents"
  headers:
    Authorization: "Bearer {access_token}"
  parameters:
    query:
      agent_type: "research"  # optional: research, codebase_analyzer, frontend, backend
      status: "available"  # optional: available, busy, offline, maintenance

response:
  status_code: 200
  body:
    agents:
      - agent_id: "research_agent_001"
        agent_type: "research"
        status: "available"
        capabilities:
          - "web_research"
          - "competitive_analysis"
          - "knowledge_synthesis"
          - "source_verification"
        supported_task_types:
          - "market_analysis"
          - "competitive_research"
          - "technology_research"
          - "academic_research"
        mcp_integrations:
          - "perplexity"
        performance_metrics:
          average_execution_time: 180  # seconds
          success_rate: 0.96
          current_load: 0.3  # 30% utilization
          max_concurrent_tasks: 3
        last_heartbeat: "2025-10-15T17:00:00Z"
      - agent_id: "codebase_analyzer_001"
        agent_type: "codebase_analyzer"
        status: "busy"
        current_tasks: 2
        capabilities:
          - "security_analysis"
          - "performance_analysis"
          - "architecture_review"
          - "dependency_mapping"
        supported_task_types:
          - "security_audit"
          - "code_review"
          - "architecture_analysis"
          - "performance_review"
        mcp_integrations:
          - "serena"
        performance_metrics:
          average_execution_time: 240  # seconds
          success_rate: 0.94
          current_load: 0.67  # 67% utilization
          max_concurrent_tasks: 3
        last_heartbeat: "2025-10-15T16:59:30Z"
```

#### 3.2 Get Agent Details

**Endpoint:** `GET /agents/{agent_id}`  
**Description:** Get detailed information about a specific agent  
**Authentication:** Required  
**Rate Limit:** 100 requests per minute

```yaml
request:
  method: "GET"
  path: "/agents/{agent_id}"
  headers:
    Authorization: "Bearer {access_token}"
  parameters:
    path:
      agent_id: string  # Agent ID

response:
  status_code: 200
  body:
    agent_id: "research_agent_001"
    agent_type: "research"
    status: "available"
    version: "1.0.0"
    created_at: "2025-10-15T16:00:00Z"
    last_updated: "2025-10-15T16:30:00Z"
    capabilities:
      - "web_research"
      - "competitive_analysis"
      - "knowledge_synthesis"
      - "source_verification"
      - "trend_analysis"
    supported_task_types:
      - "market_analysis"
      - "competitive_research"
      - "technology_research"
      - "academic_research"
    mcp_integrations:
      - server_name: "perplexity"
        status: "operational"
        last_check: "2025-10-15T17:00:00Z"
        available_methods: ["research", "search", "analyze"]
    configuration:
      max_complexity: 8
      max_concurrent_tasks: 3
      timeout: 300  # seconds
      retry_attempts: 2
    performance_metrics:
      total_tasks_completed: 156
      average_execution_time: 180  # seconds
      success_rate: 0.96
      current_load: 0.3  # 30% utilization
      uptime_percentage: 0.998
    current_tasks:
      - task_id: "task_123456789"
        progress: 0.65
        estimated_completion: "2025-10-15T17:05:00Z"
    system_prompt:
      file: "research_agent.md"
      last_loaded: "2025-10-15T16:30:00Z"
      version: "1.2.0"

error_responses:
  404:
    description: "Agent not found"
    body:
      error: "AGENT_NOT_FOUND"
      message: "Agent with specified ID not found"
```

### 4. System Prompt Management APIs

#### 4.1 Get System Prompt

**Endpoint:** `GET /system-prompts/{agent_type}`  
**Description:** Get current system prompt for agent type  
**Authentication:** Required  
**Rate Limit:** 100 requests per minute

```yaml
request:
  method: "GET"
  path: "/system-prompts/{agent_type}"
  headers:
    Authorization: "Bearer {access_token}"
  parameters:
    path:
      agent_type: string  # research, codebase_analyzer, frontend, backend, team_leader
    query:
      task_type: "market_analysis"  # optional

response:
  status_code: 200
  body:
    agent_type: "research"
    task_type: "market_analysis"
    prompt_content: |
      # Research Agent - Market Analysis Specialist

      You are a specialized research agent focused on market analysis and competitive intelligence. Your expertise includes:

      ## Core Capabilities
      - Comprehensive market research and analysis
      - Competitive intelligence gathering
      - Industry trend identification
      - Data-driven insights and recommendations

      ## Research Methodology
      1. **Multi-source Research**: Gather information from diverse, credible sources
      2. **Data Verification**: Cross-reference findings across multiple sources
      3. **Trend Analysis**: Identify patterns and trends in the data
      4. **Synthesis**: Combine findings into actionable insights

      ## Quality Standards
      - Always provide source attribution
      - Include confidence scoring for findings
      - Highlight assumptions and limitations
      - Ensure recommendations are data-driven

      ## Current Task: Market Analysis
      Focus on analyzing market trends, competitive landscape, and opportunities in the specified domain.
    file_path: "system_prompts/research_market_analysis.md"
    version: "1.2.0"
    last_modified: "2025-10-15T16:30:00Z"
    checksum: "sha256:abc123..."
    metadata:
      word_count: 450
      sections: 12
      examples_count: 5

error_responses:
  404:
    description: "System prompt not found"
    body:
      error: "PROMPT_NOT_FOUND"
      message: "System prompt not found for specified agent and task type"
```

#### 4.2 Update System Prompt

**Endpoint:** `PUT /system-prompts/{agent_type}`  
**Description:** Update system prompt for agent type  
**Authentication:** Required  
**Rate Limit:** 10 requests per minute

```yaml
request:
  method: "PUT"
  path: "/system-prompts/{agent_type}"
  headers:
    Authorization: "Bearer {access_token}"
    Content-Type: "application/json"
  parameters:
    path:
      agent_type: string  # research, codebase_analyzer, frontend, backend, team_leader
    query:
      task_type: "market_analysis"  # optional
  body:
    prompt_content: |
      # Updated Research Agent Prompt
      
      Updated content...
    metadata:
      version: "1.3.0"
      change_description: "Added new market analysis methodologies"
      author: "user_123456789"

response:
  status_code: 200
  body:
    agent_type: "research"
    task_type: "market_analysis"
    file_path: "system_prompts/research_market_analysis.md"
    previous_version: "1.2.0"
    new_version: "1.3.0"
    updated_at: "2025-10-15T17:00:00Z"
    checksum: "sha256:def456..."
    hot_reloaded: true
    affected_agents: ["research_agent_001", "research_agent_002"]

error_responses:
  400:
    description: "Invalid prompt content"
    body:
      error: "INVALID_PROMPT_CONTENT"
      message: "Prompt content validation failed"
      details:
        issue: "Prompt must include role definition and capabilities"
  403:
    description: "Insufficient permissions"
    body:
      error: "INSUFFICIENT_PERMISSIONS"
      message: "User does not have permission to update system prompts"
```

### 5. MCP Server Management APIs

#### 5.1 List MCP Servers

**Endpoint:** `GET /mcp/servers`  
**Description:** List all configured MCP servers and their status  
**Authentication:** Required  
**Rate Limit:** 50 requests per minute

```yaml
request:
  method: "GET"
  path: "/mcp/servers"
  headers:
    Authorization: "Bearer {access_token}"
  parameters:
    query:
      status: "operational"  # optional: operational, degraded, error, disabled

response:
  status_code: 200
  body:
    servers:
      - server_name: "perplexity"
        server_type: "research"
        status: "operational"
        version: "1.0.0"
        last_health_check: "2025-10-15T17:00:00Z"
        response_time: 0.125  # seconds
        success_rate: 0.98
        available_methods:
          - "research"
          - "search"
          - "analyze"
          - "summarize"
        configuration:
          timeout: 5  # seconds
          retry_attempts: 3
          complexity_level: "medium"
        usage_stats:
          total_requests: 1250
          successful_requests: 1225
          failed_requests: 25
          average_response_time: 0.15  # seconds
      - server_name: "serena"
        server_type: "code_analysis"
        status: "operational"
        version: "1.2.0"
        last_health_check: "2025-10-15T16:59:30Z"
        response_time: 0.25  # seconds
        success_rate: 0.96
        available_methods:
          - "analyze_code"
          - "security_scan"
          - "performance_review"
          - "architecture_analysis"
        configuration:
          timeout: 10  # seconds
          retry_attempts: 2
          analysis_depth: "comprehensive"
        usage_stats:
          total_requests: 850
          successful_requests: 816
          failed_requests: 34
          average_response_time: 0.30  # seconds
```

#### 5.2 Test MCP Server Connection

**Endpoint:** `POST /mcp/servers/{server_name}/test`  
**Description:** Test connection to specific MCP server  
**Authentication:** Required  
**Rate Limit:** 10 requests per minute

```yaml
request:
  method: "POST"
  path: "/mcp/servers/{server_name}/test"
  headers:
    Authorization: "Bearer {access_token}"
  parameters:
    path:
      server_name: string  # MCP server name
  body:
    test_method: "ping"  # ping, echo, method_test
    method_params: {}  # optional parameters for method testing

response:
  status_code: 200
  body:
    server_name: "perplexity"
    test_result: "success"
    response_time: 0.125  # seconds
    timestamp: "2025-10-15T17:00:00Z"
    details:
      connection_status: "established"
      authentication: "successful"
      method_availability: "confirmed"
      server_version: "1.0.0"
    test_details:
      test_type: "ping"
      request_sent: "2025-10-15T17:00:00.000Z"
      response_received: "2025-10-15T17:00:00.125Z"
      data_exchanged: 64  # bytes

error_responses:
  404:
    description: "MCP server not found"
    body:
      error: "MCP_SERVER_NOT_FOUND"
      message: "MCP server with specified name not found"
  503:
    description: "MCP server unavailable"
    body:
      error: "MCP_SERVER_UNAVAILABLE"
      message: "MCP server is currently unavailable"
      details:
        connection_error: "Connection timeout"
        retry_after: 30  # seconds
```

### 6. Authentication and Authorization APIs

#### 6.1 OAuth2 Token Exchange

**Endpoint:** `POST /auth/oauth2/token`  
**Description:** Exchange authorization code for access token  
**Authentication:** None (public endpoint)  
**Rate Limit:** 20 requests per minute

```yaml
request:
  method: "POST"
  path: "/auth/oauth2/token"
  headers:
    Content-Type: "application/x-www-form-urlencoded"
  body:
    grant_type: "authorization_code"
    code: "auth_code_123456789"
    redirect_uri: "http://localhost:8000/auth/callback"
    client_id: "client_123456789"
    client_secret: "client_secret_abc123"
    code_verifier: "code_verifier_def456"  # optional for PKCE

response:
  status_code: 200
  body:
    access_token: "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."
    token_type: "Bearer"
    expires_in: 3600  # seconds
    refresh_token: "refresh_token_ghi789"
    scope: "read write agent:execute"
    id_token: "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."  # optional

error_responses:
  400:
    description: "Invalid request"
    body:
      error: "invalid_request"
      error_description: "Missing required parameter: grant_type"
  401:
    description: "Invalid client credentials"
    body:
      error: "invalid_client"
      error_description: "Client authentication failed"
```

#### 6.2 Refresh Access Token

**Endpoint:** `POST /auth/oauth2/refresh`  
**Description:** Refresh access token using refresh token  
**Authentication:** None (public endpoint)  
**Rate Limit:** 10 requests per minute

```yaml
request:
  method: "POST"
  path: "/auth/oauth2/refresh"
  headers:
    Content-Type: "application/x-www-form-urlencoded"
  body:
    grant_type: "refresh_token"
    refresh_token: "refresh_token_ghi789"
    client_id: "client_123456789"
    client_secret: "client_secret_abc123"

response:
  status_code: 200
  body:
    access_token: "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."
    token_type: "Bearer"
    expires_in: 3600  # seconds
    refresh_token: "refresh_token_jkl012"  # optional, may be same
    scope: "read write agent:execute"

error_responses:
  401:
    description: "Invalid refresh token"
    body:
      error: "invalid_grant"
      error_description: "Refresh token is invalid or expired"
```

#### 6.3 Get User Info

**Endpoint:** `GET /auth/userinfo`  
**Description:** Get information about authenticated user  
**Authentication:** Required  
**Rate Limit:** 100 requests per minute

```yaml
request:
  method: "GET"
  path: "/auth/userinfo"
  headers:
    Authorization: "Bearer {access_token}"

response:
  status_code: 200
  body:
    sub: "user_123456789"
    email: "user@example.com"
    name: "John Doe"
    picture: "https://example.com/avatar.jpg"
    email_verified: true
    roles:
      - "agent_user"
      - "task_creator"
    permissions:
      - "agent:execute"
      - "task:create"
      - "task:read"
      - "system_prompt:read"
    metadata:
      provider: "google"
      created_at: "2025-10-01T12:00:00Z"
      last_login: "2025-10-15T16:45:00Z"

error_responses:
  401:
    description: "Invalid or expired token"
    body:
      error: "INVALID_TOKEN"
      message: "Access token is invalid or has expired"
```

### 7. System Administration APIs

#### 7.1 Health Check

**Endpoint:** `GET /health`  
**Description:** Get overall system health status  
**Authentication:** None (public endpoint)  
**Rate Limit:** 100 requests per minute

```yaml
request:
  method: "GET"
  path: "/health"

response:
  status_code: 200
  body:
    status: "healthy"  # healthy, degraded, unhealthy
    timestamp: "2025-10-15T17:00:00Z"
    uptime: 86400  # seconds
    version: "1.0.0"
    components:
      team_leader:
        status: "healthy"
        response_time: 0.025  # seconds
        uptime: 86400  # seconds
      websocket_server:
        status: "healthy"
        active_connections: 15
        response_time: 0.010  # seconds
      database:
        status: "healthy"
        response_time: 0.005  # seconds
        connection_pool: "8/20 active"
      mcp_servers:
        perplexity:
          status: "healthy"
          response_time: 0.125  # seconds
        serena:
          status: "healthy"
          response_time: 0.250  # seconds
      authentication:
        status: "healthy"
        oauth_providers: "operational"
    performance_metrics:
      memory_usage: 1.2  # GB
      cpu_usage: 0.15  # 15%
      disk_usage: 0.35  # 35%
      network_io: 0.5  # MB/s
    recent_metrics:
      requests_per_minute: 45
      average_response_time: 0.15  # seconds
      error_rate: 0.02  # 2%
      active_tasks: 8

error_responses:
  503:
    description: "System unhealthy"
    body:
      status: "unhealthy"
      timestamp: "2025-10-15T17:00:00Z"
      issues:
        - component: "mcp_servers.perplexity"
          status: "error"
          error: "Connection timeout"
        - component: "database"
          status: "degraded"
          error: "High connection pool usage"
```

#### 7.2 Get System Metrics

**Endpoint:** `GET /metrics`  
**Description:** Get detailed system performance metrics  
**Authentication:** Required  
**Rate Limit:** 50 requests per minute

```yaml
request:
  method: "GET"
  path: "/metrics"
  headers:
    Authorization: "Bearer {access_token}"
  parameters:
    query:
      timeframe: "1h"  # 5m, 15m, 1h, 6h, 24h
      metrics: "all"  # all, performance, usage, errors

response:
  status_code: 200
  body:
    timeframe: "1h"
    timestamp: "2025-10-15T17:00:00Z"
    performance_metrics:
      response_times:
        avg: 0.15  # seconds
        p50: 0.12
        p95: 0.28
        p99: 0.45
      throughput:
        requests_per_minute: 45
        tasks_per_hour: 120
        concurrent_tasks: 8
      resource_usage:
        memory:
          current: 1.2  # GB
          peak: 1.5  # GB
          average: 1.3  # GB
        cpu:
          current: 0.15  # 15%
          peak: 0.35  # 35%
          average: 0.20  # 20%
        disk:
          current: 0.35  # 35%
          peak: 0.40  # 40%
    usage_metrics:
      agents:
        total: 4
        active: 4
        utilization: 0.65  # 65%
      tasks:
        total_completed: 156
        success_rate: 0.96
        average_execution_time: 180  # seconds
      mcp_servers:
        total_requests: 1250
        success_rate: 0.97
        average_response_time: 0.18  # seconds
    error_metrics:
      total_errors: 25
      error_rate: 0.02  # 2%
      error_types:
        timeout: 40  # 40%
        connection_error: 30  # 30%
        authentication_error: 20  # 20%
        other: 10  # 10%
      recent_errors:
        - timestamp: "2025-10-15T16:58:00Z"
          error_type: "timeout"
          component: "mcp_servers.perplexity"
          message: "Request timeout after 5 seconds"
          resolved: true
```

## WebSocket API Specifications

### Connection Establishment

```yaml
endpoint: "ws://localhost:8080/ws"
protocol: "WebSocket (RFC 6455)"
authentication: "Token-based via query parameter or subprotocol"
subprotocols: ["ai-agent-sdk-v1"]
```

#### Connection Request

```yaml
connection_url: "ws://localhost:8080/ws?token={access_token}"
headers:
  Sec-WebSocket-Protocol: "ai-agent-sdk-v1"
  Origin: "http://localhost:8000"
```

#### Connection Response

```yaml
status_code: 101
headers:
  Upgrade: "websocket"
  Connection: "upgrade"
  Sec-WebSocket-Accept: "{accept_key}"
  Sec-WebSocket-Protocol: "ai-agent-sdk-v1"
```

### Message Protocol

#### Message Format

```yaml
message_format:
  type: "JSON"
  compression: "permessage-deflate"
  encoding: "UTF-8"

message_schema:
  type: object
  required: ["message_id", "type", "timestamp"]
  properties:
    message_id:
      type: string
      format: uuid
    type:
      type: string
      enum: ["task_assignment", "task_result", "status_update", "heartbeat", "error"]
    sender:
      type: string
      description: "Agent or client identifier"
    recipient:
      type: string
      description: "Target agent or client (optional for broadcasts)"
    timestamp:
      type: string
      format: date-time
    correlation_id:
      type: string
      format: uuid
      description: "Correlates request/response pairs"
    priority:
      type: integer
      minimum: 1
      maximum: 10
      default: 5
    requires_ack:
      type: boolean
      default: true
    payload:
      type: object
      description: "Message-specific data"
```

### 1. Task Assignment Messages

#### Task Assignment

```yaml
message_type: "task_assignment"
direction: "TeamLeader → Agent"
description: "Assign task to specific agent"

payload_schema:
  type: object
  required: ["task_id", "task_spec", "context"]
  properties:
    task_id:
      type: string
      format: uuid
    task_spec:
      $ref: "#/components/schemas/TaskSpec"
    context:
      $ref: "#/components/schemas/AgentContext"
    timeout:
      type: integer
      description: "Task timeout in seconds"

example:
  message_id: "msg_123456789"
  type: "task_assignment"
  sender: "team_leader_001"
  recipient: "research_agent_001"
  timestamp: "2025-10-15T17:00:00Z"
  correlation_id: "corr_abc123"
  priority: 7
  requires_ack: true
  payload:
    task_id: "task_123456789"
    task_spec:
      agent_type: "research"
      task_type: "market_analysis"
      task: "Analyze current AI agent coordination market trends"
      complexity: 5
      priority: 7
      project_id: "proj_123456789"
    context:
      system_prompt: "You are a research agent..."
      history: []
      mcp_context:
        perplexity: { "authenticated": true, "complexity_level": "medium" }
      metadata: {}
    timeout: 300
```

#### Task Assignment Acknowledgment

```yaml
message_type: "task_ack"
direction: "Agent → TeamLeader"
description: "Acknowledge task assignment"

payload_schema:
  type: object
  required: ["task_id", "status"]
  properties:
    task_id:
      type: string
      format: uuid
    status:
      type: string
      enum: ["accepted", "rejected", "deferred"]
    reason:
      type: string
      description: "Reason for rejection or deferral"
    estimated_start:
      type: string
      format: date-time
      description: "Estimated start time for deferred tasks"

example:
  message_id: "msg_123456790"
  type: "task_ack"
  sender: "research_agent_001"
  recipient: "team_leader_001"
  timestamp: "2025-10-15T17:00:01Z"
  correlation_id: "corr_abc123"
  priority: 7
  requires_ack: false
  payload:
    task_id: "task_123456789"
    status: "accepted"
```

### 2. Task Result Messages

#### Task Result

```yaml
message_type: "task_result"
direction: "Agent → TeamLeader"
description: "Report task completion result"

payload_schema:
  type: object
  required: ["task_id", "status", "result"]
  properties:
    task_id:
      type: string
      format: uuid
    status:
      type: string
      enum: ["completed", "failed", "partial"]
    result:
      $ref: "#/components/schemas/TaskResult"
    execution_metrics:
      type: object
      properties:
        execution_time:
          type: number
          format: float
        tokens_used:
          type: integer
        mcp_calls:
          type: integer
        api_calls:
          type: integer

example:
  message_id: "msg_123456791"
  type: "task_result"
  sender: "research_agent_001"
  recipient: "team_leader_001"
  timestamp: "2025-10-15T17:04:45Z"
  correlation_id: "corr_abc123"
  priority: 7
  requires_ack: true
  payload:
    task_id: "task_123456789"
    status: "completed"
    result:
      content: "Market analysis shows rapid growth..."
      confidence_score: 0.87
      sources:
        - title: "Enterprise AI Adoption Survey 2024"
          url: "https://example.com/survey"
          credibility: 0.95
      metadata:
        word_count: 1250
        sources_count: 8
    execution_metrics:
      execution_time: 285
      tokens_used: 1500
      mcp_calls: 3
      api_calls: 12
```

#### Task Result Acknowledgment

```yaml
message_type: "task_result_ack"
direction: "TeamLeader → Agent"
description: "Acknowledge task result receipt"

payload_schema:
  type: object
  required: ["task_id", "received"]
  properties:
    task_id:
      type: string
      format: uuid
    received:
      type: boolean
    quality_check:
      type: object
      properties:
        passed:
          type: boolean
        issues:
          type: array
          items:
            type: string

example:
  message_id: "msg_123456792"
  type: "task_result_ack"
  sender: "team_leader_001"
  recipient: "research_agent_001"
  timestamp: "2025-10-15T17:04:46Z"
  correlation_id: "corr_abc123"
  priority: 7
  requires_ack: false
  payload:
    task_id: "task_123456789"
    received: true
    quality_check:
      passed: true
      issues: []
```

### 3. Status Update Messages

#### Agent Status Update

```yaml
message_type: "status_update"
direction: "Agent → TeamLeader"
description: "Report agent status and health"

payload_schema:
  type: object
  required: ["agent_id", "status", "load"]
  properties:
    agent_id:
      type: string
    status:
      type: string
      enum: ["available", "busy", "offline", "maintenance", "error"]
    load:
      type: number
      minimum: 0
      maximum: 1
    current_tasks:
      type: array
      items:
        type: object
        properties:
          task_id:
            type: string
          progress:
            type: number
            minimum: 0
            maximum: 1
    capabilities:
      type: array
      items:
        type: string
    performance_metrics:
      type: object
      properties:
        average_response_time:
          type: number
          format: float
        success_rate:
          type: number
          format: float
        uptime:
          type: number
          format: float

example:
  message_id: "msg_123456793"
  type: "status_update"
  sender: "research_agent_001"
  recipient: "team_leader_001"
  timestamp: "2025-10-15T17:05:00Z"
  priority: 3
  requires_ack: false
  payload:
    agent_id: "research_agent_001"
    status: "available"
    load: 0.3
    current_tasks: []
    capabilities: ["web_research", "competitive_analysis", "knowledge_synthesis"]
    performance_metrics:
      average_response_time: 180
      success_rate: 0.96
      uptime: 0.998
```

#### System Status Update

```yaml
message_type: "system_status"
direction: "TeamLeader → All Agents"
description: "Broadcast system status information"

payload_schema:
  type: object
  required: ["system_status", "timestamp"]
  properties:
    system_status:
      type: string
      enum: ["normal", "degraded", "maintenance", "emergency"]
    message:
      type: string
      description: "Status message for agents"
    affected_components:
      type: array
      items:
        type: string
    estimated_recovery:
      type: string
      format: date-time
      description: "Estimated recovery time"

example:
  message_id: "msg_123456794"
  type: "system_status"
  sender: "team_leader_001"
  recipient: "broadcast"
  timestamp: "2025-10-15T17:05:00Z"
  priority: 8
  requires_ack: false
  payload:
    system_status: "degraded"
    message: "Perplexity MCP server experiencing high latency"
    affected_components: ["mcp_servers.perplexity"]
    estimated_recovery: "2025-10-15T17:10:00Z"
```

### 4. Heartbeat Messages

#### Agent Heartbeat

```yaml
message_type: "heartbeat"
direction: "Agent → TeamLeader"
description: "Periodic heartbeat to maintain connection"

payload_schema:
  type: object
  required: ["agent_id", "timestamp"]
  properties:
    agent_id:
      type: string
    timestamp:
      type: string
      format: date-time
    status:
      type: string
      enum: ["alive", "busy", "idle"]
    queue_size:
      type: integer
      description: "Number of pending tasks"
    memory_usage:
      type: number
      description: "Memory usage in MB"

example:
  message_id: "msg_123456795"
  type: "heartbeat"
  sender: "research_agent_001"
  recipient: "team_leader_001"
  timestamp: "2025-10-15T17:05:00Z"
  priority: 1
  requires_ack: false
  payload:
    agent_id: "research_agent_001"
    timestamp: "2025-10-15T17:05:00Z"
    status: "alive"
    queue_size: 0
    memory_usage: 256
```

#### Heartbeat Response

```yaml
message_type: "heartbeat_ack"
direction: "TeamLeader → Agent"
description: "Response to agent heartbeat"

payload_schema:
  type: object
  required: ["received_timestamp", "server_timestamp"]
  properties:
    received_timestamp:
      type: string
      format: date-time
    server_timestamp:
      type: string
      format: date-time
    instructions:
      type: array
      items:
        type: string
      description: "Any instructions for the agent"

example:
  message_id: "msg_123456796"
  type: "heartbeat_ack"
  sender: "team_leader_001"
  recipient: "research_agent_001"
  timestamp: "2025-10-15T17:05:00Z"
  priority: 1
  requires_ack: false
  payload:
    received_timestamp: "2025-10-15T17:05:00Z"
    server_timestamp: "2025-10-15T17:05:00Z"
    instructions: []
```

### 5. Error Messages

#### Error Report

```yaml
message_type: "error"
direction: "Any → Any"
description: "Report error conditions"

payload_schema:
  type: object
  required: ["error_code", "message", "timestamp"]
  properties:
    error_code:
      type: string
      enum: ["TASK_EXECUTION_FAILED", "AGENT_OVERLOAD", "MCP_SERVER_ERROR", "AUTHENTICATION_ERROR", "SYSTEM_ERROR"]
    message:
      type: string
      description: "Human-readable error message"
    details:
      type: object
      description: "Additional error details"
    task_id:
      type: string
      format: uuid
      description: "Related task ID if applicable"
    component:
      type: string
      description: "Component where error occurred"
    severity:
      type: string
      enum: ["low", "medium", "high", "critical"]
    recoverable:
      type: boolean
      description: "Whether error is recoverable"

example:
  message_id: "msg_123456797"
  type: "error"
  sender: "research_agent_001"
  recipient: "team_leader_001"
  timestamp: "2025-10-15T17:05:00Z"
  correlation_id: "corr_abc123"
  priority: 9
  requires_ack: true
  payload:
    error_code: "MCP_SERVER_ERROR"
    message: "Perplexity MCP server timeout during research query"
    details:
      timeout_duration: 5
      query: "AI agent coordination market trends"
      server_response: "Connection timeout"
    task_id: "task_123456789"
    component: "mcp_client.perplexity"
    severity: "medium"
    recoverable: true
```

## MCP Integration API Specifications

### MCP Protocol Configuration

```yaml
protocol: "JSON-RPC 2.0"
transport: "stdio/HTTP"
encoding: "UTF-8"
authentication: "API Key/OAuth2"
```

### 1. Perplexity MCP Server API

#### Research Method

```yaml
method_name: "research"
description: "Execute comprehensive research query"
parameters:
  type: object
  required: ["query"]
  properties:
    query:
      type: string
      description: "Research query"
      minLength: 10
      maxLength: 1000
    complexity_level:
      type: string
      enum: ["low", "medium", "high"]
      default: "medium"
      description: "Research complexity and depth"
    research_mode:
      type: string
      enum: ["comprehensive", "targeted", "competitive", "academic"]
      default: "comprehensive"
      description: "Type of research to perform"
    max_sources:
      type: integer
      minimum: 5
      maximum: 50
      default: 20
      description: "Maximum number of sources to analyze"
    include_analysis:
      type: boolean
      default: true
      description: "Include AI analysis of findings"
    time_range:
      type: string
      enum: ["last_day", "last_week", "last_month", "last_year", "all_time"]
      default: "last_month"
      description: "Time range for research"

response_schema:
  type: object
  required: ["status", "query", "results"]
  properties:
    status:
      type: string
      enum: ["success", "error", "partial"]
    query:
      type: string
    results:
      type: object
      properties:
        summary:
          type: string
          description: "Research summary and key findings"
        sources:
          type: array
          items:
            type: object
            properties:
              title:
                type: string
              url:
                type: string
                format: uri
              snippet:
                type: string
              credibility_score:
                type: number
                minimum: 0
                maximum: 1
              published_date:
                type: string
                format: date-time
        analysis:
          type: object
          properties:
            key_trends:
              type: array
              items:
                type: string
            insights:
              type: array
              items:
                type: string
            confidence_score:
              type: number
              minimum: 0
              maximum: 1
        metadata:
          type: object
          properties:
            total_sources_found:
              type: integer
            sources_analyzed:
              type: integer
            completion_time:
              type: number
              format: float
            api_calls_made:
              type: integer

example_request:
  jsonrpc: "2.0"
  method: "research"
  params:
    query: "AI agent coordination market trends 2024"
    complexity_level: "medium"
    research_mode: "comprehensive"
    max_sources: 20
    include_analysis: true
    time_range: "last_year"
  id: "req_123456789"

example_response:
  jsonrpc: "2.0"
  result:
    status: "success"
    query: "AI agent coordination market trends 2024"
    results:
      summary: "The AI agent coordination market is experiencing rapid growth with a CAGR of 51.3%..."
      sources:
        - title: "Enterprise AI Adoption Survey 2024"
          url: "https://example.com/survey"
          snippet: "71% of enterprises report coordination challenges in AI agent deployment..."
          credibility_score: 0.95
          published_date: "2024-03-15T10:00:00Z"
      analysis:
        key_trends:
          - "Hierarchical coordination patterns becoming dominant"
          - "Enterprise adoption driving standardization"
          - "Security and compliance as key differentiators"
        insights:
          - "Market growing from $5.25B in 2024 to $52.62B by 2030"
          - "90.2% performance improvement with multi-agent systems"
        confidence_score: 0.87
      metadata:
        total_sources_found: 156
        sources_analyzed: 20
        completion_time: 2.45
        api_calls_made: 12
  id: "req_123456789"
```

#### Search Method

```yaml
method_name: "search"
description: "Quick search for specific information"
parameters:
  type: object
  required: ["query"]
  properties:
    query:
      type: string
      description: "Search query"
      minLength: 5
      maxLength: 500
    max_results:
      type: integer
      minimum: 1
      maximum: 20
      default: 10
      description: "Maximum number of results to return"
    search_type:
      type: string
      enum: ["web", "news", "academic", "technical"]
      default: "web"
      description: "Type of search to perform"
    safe_search:
      type: boolean
      default: true
      description: "Enable safe search filtering"

response_schema:
  type: object
  required: ["status", "query", "results"]
  properties:
    status:
      type: string
      enum: ["success", "error"]
    query:
      type: string
    results:
      type: array
      items:
        type: object
        properties:
          title:
            type: string
          url:
            type: string
            format: uri
          snippet:
            type: string
          relevance_score:
            type: number
            minimum: 0
            maximum: 1
          published_date:
            type: string
            format: date-time

example_request:
  jsonrpc: "2.0"
  method: "search"
  params:
    query: "Claude SDK multi-agent coordination"
    max_results: 10
    search_type: "technical"
  id: "req_123456790"

example_response:
  jsonrpc: "2.0"
  result:
    status: "success"
    query: "Claude SDK multi-agent coordination"
    results:
      - title: "Claude Agent SDK Documentation"
        url: "https://docs.anthropic.com/claude/docs/agents"
        snippet: "The Claude Agent SDK provides tools for building sophisticated multi-agent systems..."
        relevance_score: 0.92
        published_date: "2024-10-01T00:00:00Z"
  id: "req_123456790"
```

### 2. Serena MCP Server API

#### Analyze Code Method

```yaml
method_name: "analyze_code"
description: "Analyze code repository for security, performance, and architecture"
parameters:
  type: object
  required: ["repository_path"]
  properties:
    repository_path:
      type: string
      description: "Path to code repository"
    analysis_type:
      type: string
      enum: ["comprehensive", "security", "performance", "architecture", "security_focused"]
      default: "comprehensive"
      description: "Type of analysis to perform"
    include_suggestions:
      type: boolean
      default: true
      description: "Include improvement suggestions"
    check_security:
      type: boolean
      default: true
      description: "Perform security vulnerability scanning"
    file_patterns:
      type: array
      items:
        type: string
      description: "File patterns to include in analysis"
      default: ["**/*.py", "**/*.js", "**/*.ts", "**/*.java"]
    exclude_patterns:
      type: array
      items:
        type: string
      description: "File patterns to exclude from analysis"
      default: ["**/test/**", "**/node_modules/**", "**/.git/**"]

response_schema:
  type: object
  required: ["status", "repository_path", "analysis_type"]
  properties:
    status:
      type: string
      enum: ["success", "error", "partial"]
    repository_path:
      type: string
    analysis_type:
      type: string
    findings:
      type: object
      properties:
        security:
          type: object
          properties:
            vulnerabilities:
              type: array
              items:
                type: object
                properties:
                  severity:
                    type: string
                    enum: ["low", "medium", "high", "critical"]
                  description:
                    type: string
                  file_path:
                    type: string
                  line_number:
                    type: integer
                  cwe_id:
                    type: string
            security_score:
              type: number
              minimum: 0
              maximum: 10
        performance:
          type: object
          properties:
            bottlenecks:
              type: array
              items:
                type: object
                properties:
                  type:
                    type: string
                    enum: ["cpu", "memory", "io", "network"]
                  description:
                    type: string
                  file_path:
                    type: string
                  impact:
                    type: string
                    enum: ["low", "medium", "high"]
            performance_score:
              type: number
              minimum: 0
              maximum: 10
        architecture:
          type: object
          properties:
            patterns:
              type: array
              items:
                type: object
                properties:
                  pattern:
                    type: string
                  file_path:
                    type: string
                  confidence:
                    type: number
                    minimum: 0
                    maximum: 1
            architecture_score:
              type: number
              minimum: 0
              maximum: 10
    suggestions:
      type: array
      items:
        type: object
        properties:
          category:
            type: string
            enum: ["security", "performance", "architecture", "best_practices"]
          priority:
            type: string
            enum: ["low", "medium", "high"]
          description:
            type: string
          file_path:
            type: string
          effort_estimate:
            type: string
            enum: ["quick", "moderate", "significant"]
    metrics:
      type: object
      properties:
        files_analyzed:
          type: integer
        lines_of_code:
          type: integer
        complexity_score:
          type: number
        duplicate_code_percentage:
          type: number
        test_coverage:
          type: number
        completion_time:
          type: number
          format: float

example_request:
  jsonrpc: "2.0"
  method: "analyze_code"
  params:
    repository_path: "/path/to/repository"
    analysis_type: "comprehensive"
    include_suggestions: true
    check_security: true
    file_patterns: ["**/*.py", "**/*.js"]
    exclude_patterns: ["**/test/**"]
  id: "req_123456791"

example_response:
  jsonrpc: "2.0"
  result:
    status: "success"
    repository_path: "/path/to/repository"
    analysis_type: "comprehensive"
    findings:
      security:
        vulnerabilities:
          - severity: "medium"
            description: "Potential SQL injection vulnerability"
            file_path: "src/database.py"
            line_number: 45
            cwe_id: "CWE-89"
        security_score: 7.5
      performance:
        bottlenecks:
          - type: "memory"
            description: "Potential memory leak in loop"
            file_path: "src/processor.py"
            impact: "medium"
        performance_score: 8.0
      architecture:
        patterns:
          - pattern: "singleton"
            file_path: "src/config.py"
            confidence: 0.95
        architecture_score: 8.5
    suggestions:
      - category: "security"
        priority: "high"
        description: "Implement parameterized queries to prevent SQL injection"
        file_path: "src/database.py"
        effort_estimate: "moderate"
    metrics:
      files_analyzed: 25
      lines_of_code: 5432
      complexity_score: 6.8
      duplicate_code_percentage: 12.5
      test_coverage: 78.0
      completion_time: 3.2
  id: "req_123456791"
```

#### Security Scan Method

```yaml
method_name: "security_scan"
description: "Focused security vulnerability scanning"
parameters:
  type: object
  required: ["repository_path"]
  properties:
    repository_path:
      type: string
      description: "Path to code repository"
    scan_level:
      type: string
      enum: ["quick", "standard", "comprehensive"]
      default: "standard"
      description: "Depth of security scan"
    vulnerability_types:
      type: array
      items:
        type: string
        enum: ["injection", "xss", "csrf", "authentication", "authorization", "crypto", "config"]
      description: "Types of vulnerabilities to check"
    include_dependencies:
      type: boolean
      default: true
      description: "Include dependency vulnerability scanning"

response_schema:
  type: object
  required: ["status", "vulnerabilities", "security_score"]
  properties:
    status:
      type: string
      enum: ["success", "error"]
    vulnerabilities:
      type: array
      items:
        type: object
        properties:
          id:
            type: string
          severity:
            type: string
            enum: ["info", "low", "medium", "high", "critical"]
          title:
            type: string
          description:
            type: string
          file_path:
            type: string
          line_number:
            type: integer
          cwe_id:
            type: string
          cvss_score:
            type: number
          remediation:
            type: string
          references:
            type: array
            items:
              type: string
    security_score:
      type: number
      minimum: 0
      maximum: 10
    summary:
      type: object
      properties:
        total_vulnerabilities:
          type: integer
        critical_count:
          type: integer
        high_count:
          type: integer
        medium_count:
          type: integer
        low_count:
          type: integer
        info_count:
          type: integer
    scan_metadata:
      type: object
      properties:
        scan_duration:
          type: number
          format: float
        files_scanned:
          type: integer
        lines_analyzed:
          type: integer
        dependencies_checked:
          type: integer

example_request:
  jsonrpc: "2.0"
  method: "security_scan"
  params:
    repository_path: "/path/to/repository"
    scan_level: "standard"
    vulnerability_types: ["injection", "authentication", "crypto"]
    include_dependencies: true
  id: "req_123456792"

example_response:
  jsonrpc: "2.0"
  result:
    status: "success"
    vulnerabilities:
      - id: "vuln_001"
        severity: "high"
        title: "SQL Injection Vulnerability"
        description: "User input not properly sanitized before database query"
        file_path: "src/auth.py"
        line_number: 67
        cwe_id: "CWE-89"
        cvss_score: 8.1
        remediation: "Use parameterized queries or prepared statements"
        references:
          - "https://owasp.org/www-community/attacks/SQL_Injection"
    security_score: 6.5
    summary:
      total_vulnerabilities: 3
      critical_count: 0
      high_count: 1
      medium_count: 1
      low_count: 1
      info_count: 0
    scan_metadata:
      scan_duration: 2.8
      files_scanned: 25
      lines_analyzed: 5432
      dependencies_checked: 156
  id: "req_123456792"
```

## Error Handling Specifications

### HTTP Error Response Format

```yaml
error_response_schema:
  type: object
  required: ["error", "message", "timestamp"]
  properties:
    error:
      type: string
      description: "Machine-readable error code"
    message:
      type: string
      description: "Human-readable error message"
    details:
      type: object
      description: "Additional error details"
    request_id:
      type: string
      format: uuid
      description: "Request identifier for tracking"
    timestamp:
      type: string
      format: date-time
      description: "Error timestamp"
```

### WebSocket Error Message Format

```yaml
websocket_error_schema:
  type: object
  required: ["error_code", "message", "timestamp"]
  properties:
    error_code:
      type: string
      enum: ["CONNECTION_ERROR", "AUTHENTICATION_ERROR", "MESSAGE_FORMAT_ERROR", "AGENT_ERROR", "SYSTEM_ERROR"]
    message:
      type: string
      description: "Human-readable error message"
    details:
      type: object
      description: "Additional error details"
    recoverable:
      type: boolean
      description: "Whether error is recoverable"
    retry_after:
      type: integer
      description: "Suggested retry delay in seconds"
    timestamp:
      type: string
      format: date-time
```

### MCP Error Response Format

```yaml
mcp_error_response_schema:
  type: object
  required: ["error"]
  properties:
    error:
      type: object
      required: ["code", "message"]
      properties:
        code:
          type: integer
          description: "JSON-RPC error code"
        message:
          type: string
          description: "Error message"
        data:
          type: object
          description: "Additional error data"
    jsonrpc:
      type: string
      enum: ["2.0"]
    id:
      type: ["string", "number", "null"]
      description: "Request ID or null for notification"
```

---

## API Versioning and Compatibility

### Versioning Strategy

```yaml
versioning:
  type: "Semantic Versioning (semver)"
  format: "v{major}.{minor}.{patch}"
  current_version: "1.0.0"
  compatibility:
    backward_compatible: true
    deprecation_notice: "30 days"
    breaking_changes: "major version increment"
```

### API Deprecation Process

```yaml
deprecation_process:
  1. "Add deprecation warning to API responses"
  2. "Update documentation with migration guide"
  3. "Maintain backward compatibility for 30 days"
  4. "Remove deprecated endpoint in next major version"
  
notification_methods:
  - "Response headers: X-API-Deprecated, X-API-Sunset"
  - "Documentation banners"
  - "Developer email notifications"
  - "System status page updates"
```

---

## Document Status

**Status:** READY FOR CODING AGENTS  
**Validation:** All API specifications reviewed and approved  
**Completeness:** 100% - All REST, WebSocket, and MCP APIs defined  
**Traceability:** All API specifications traceable to requirements  

**Next Steps:** Coding agents should use these API specifications to implement the communication interfaces and external service integrations.
