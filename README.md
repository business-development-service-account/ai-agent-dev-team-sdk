# AI Agent Dev Team SDK - Core Foundation Infrastructure

A comprehensive SDK for building AI agent development teams with hierarchical coordination, real-time communication, and enterprise-grade security.

## Overview

The AI Agent Dev Team SDK provides a complete foundation for creating specialized AI agent teams that can coordinate complex development tasks through a structured ten-phase process. The SDK includes:

- **TeamLeader Orchestration**: Central coordination with programmatic rules engine
- **Specialized Agents**: Research, Code Analysis, Frontend, and Backend development agents
- **Real-time Communication**: WebSocket-based agent coordination
- **MCP Integration**: External service integration with fallback mechanisms
- **Enterprise Security**: OAuth2 + RBAC with comprehensive audit logging
- **Zero Mock Policy**: All code is immediately executable and verifiable

## Features

### Core Components

- **TeamLeader Agent**: Central orchestration with ten-phase development process
- **Rules Engine**: Programmatic validation and scope enforcement
- **Context Manager**: Dynamic system prompt loading with hot-reload capabilities
- **Task Orchestrator**: Comprehensive task delegation and monitoring
- **Agent Registry**: Dynamic agent capability management and health monitoring

### Specialized Agents

- **ResearchAgent**: Market research and competitive intelligence with Perplexity MCP
- **CodeBaseAnalyzer**: Security, performance, and architecture analysis with Serena MCP
- **FrontEndCoder**: Modern UI component development with responsive design
- **BackEndCoder**: Robust API development with database integration

### Integration Capabilities

- **MCP Servers**: Universal client for Perplexity, Serena, and custom servers
- **WebSocket Communication**: Real-time bidirectional messaging with acknowledgment
- **Database Integration**: PostgreSQL with comprehensive audit logging
- **Security Framework**: OAuth2 authentication with RBAC authorization

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/ai-agent-sdk/ai-agent-sdk.git
cd ai-agent-sdk

# Install dependencies using UV (recommended)
pip install uv
uv sync

# Or using pip
pip install -e .
```

### Configuration

1. **Copy environment template:**
   ```bash
   cp .env.example .env
   ```

2. **Configure API keys:**
   ```bash
   # Edit .env and add your API keys
   ANTHROPIC_API_KEY=your_anthropic_api_key
   PERPLEXITY_API_KEY=your_perplexity_api_key
   SERENA_API_KEY=your_serena_api_key
   ```

3. **Configure database (optional):**
   ```bash
   # Using Docker Compose
   docker-compose up -d postgres redis
   ```

### Basic Usage

```python
import asyncio
from ai_agent_sdk import TeamLeader

async def main():
    # Initialize TeamLeader
    async with TeamLeader() as team_leader:
        # Delegate a research task
        result = await team_leader.delegate_task(
            agent_type="research",
            task_type="market_analysis",
            task="Analyze current AI agent coordination market trends",
            complexity=5,
            priority=7
        )

        print(f"Research result: {result.content[:100]}...")

if __name__ == "__main__":
    asyncio.run(main())
```

### Advanced Usage

```python
from ai_agent_sdk import TeamLeader
from ai_agent_sdk.agents import ResearchAgent, CodeBaseAnalyzer

async def advanced_workflow():
    team_leader = TeamLeader()

    # Initialize with custom configuration
    await team_leader.initialize()

    try:
        # Phase 1: Research
        research_result = await team_leader.delegate_task(
            agent_type="research",
            task_type="competitive_research",
            task="Analyze competitive landscape in AI agent coordination",
            complexity=6
        )

        # Phase 2: Analysis
        analysis_result = await team_leader.delegate_task(
            agent_type="codebase_analyzer",
            task_type="architecture_analysis",
            task="Review architecture of existing coordination systems",
            complexity=7,
            metadata={"repository_path": "/path/to/repo"}
        )

        # Get status
        status = team_leader.get_status()
        print(f"TeamLeader status: {status}")

    finally:
        await team_leader.shutdown()

asyncio.run(advanced_workflow())
```

## Architecture

### System Overview

```
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
```

### Ten-Phase Development Process

1. **Initialization**: System setup and configuration
2. **Research**: Information gathering and synthesis
3. **Planning**: Architecture and implementation planning
4. **Context Preparation**: Context assembly and validation
5. **Validation**: Risk assessment and scope checking
6. **Implementation**: Functional development with no mocks
7. **Verification**: Independent verification and quality checks
8. **Testing**: Comprehensive testing with mock detection
9. **User Value Validation**: Final validation against requirements
10. **Documentation**: Documentation creation and next part preparation

## Configuration

### TeamLeader Configuration

```yaml
# config/team_leader.yaml
rules:
  complexity_budget: 25
  phase_timeout: 3600
  max_concurrent_tasks: 10

prompts_directory: "system_prompts"
prompt_cache_size: 1000

mcp:
  timeout: 5
  retry_attempts: 3

  servers:
    perplexity:
      enabled: true
      api_key_env: "PERPLEXITY_API_KEY"
    serena:
      enabled: true
      api_key_env: "SERENA_API_KEY"
```

### Agent Configuration

```python
# Configure agent capabilities
config = {
    "anthropic_api_key": "your_api_key",
    "claude_model": "claude-3-sonnet-20241022",
    "max_tokens": 4096,
    "temperature": 0.3,
    "max_concurrent_tasks": 3
}
```

## Development

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=html

# Run specific test
uv run pytest tests/test_team_leader.py
```

### Code Quality

```bash
# Format code
uv run black src/ tests/

# Lint code
uv run ruff check src/ tests/

# Type checking
uv run mypy src/
```

### Development Server

```bash
# Start TeamLeader development server
uv run python -m ai_agent_sdk.main

# Start with custom configuration
uv run python -m ai_agent_sdk.main --config config/custom.yaml
```

## API Reference

### TeamLeader API

```python
# Initialize TeamLeader
team_leader = TeamLeader(config_path="config/team_leader.yaml")
await team_leader.initialize()

# Delegate tasks
result = await team_leader.delegate_task(
    agent_type="research",
    task_type="market_analysis",
    task="Research query",
    complexity=5,
    priority=7
)

# Get status
status = team_leader.get_status()

# Progress phases
await team_leader.progress_to_phase("planning")
```

### Agent Status

```python
# Get agent status
status = agent.get_status()
# Returns: {
#     "agent_id": "research_agent_001",
#     "agent_type": "research",
#     "status": "online",
#     "capabilities": [...],
#     "metrics": {...}
# }
```

## Security

### Authentication

The SDK supports OAuth2 authentication with multiple providers:

- Google OAuth2
- GitHub OAuth2
- Microsoft OAuth2

### Authorization

Role-based access control (RBAC) with fine-grained permissions:

- `agent:execute` - Execute agent tasks
- `task:create` - Create new tasks
- `task:read` - Read task results
- `system_prompt:read` - Read system prompts

### Security Features

- **Input Validation**: Comprehensive validation for all inputs
- **SQL Injection Prevention**: Parameterized queries and validation
- **XSS Protection**: Input sanitization and output encoding
- **Audit Logging**: Comprehensive security event logging
- **Encryption**: TLS 1.3 for all communications

## Monitoring

### Metrics

The SDK provides comprehensive metrics collection:

```python
# Get system metrics
metrics = team_leader.get_task_queue_status()
# Returns: {
#     "active_tasks": [...],
#     "recent_tasks": [...],
#     "metrics": {...}
# }
```

### Health Checks

```python
# Health check endpoint
health = await team_leader.get_status()
# Includes system health, component status, and performance metrics
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow Python 3.11+ async/await patterns
- Use comprehensive error handling and logging
- Write tests for all new functionality
- Follow the zero mock data policy
- Keep files under 500 lines with single responsibilities

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For questions and support:

- Create an issue on GitHub
- Check the [documentation](https://ai-agent-sdk.readthedocs.io)
- Review the [examples](examples/) directory

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a list of changes and version history.