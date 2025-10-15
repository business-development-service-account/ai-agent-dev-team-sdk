# Part 1: Core Foundation Infrastructure - Reference Research Results

**Created:** 2025-10-15 15:30:00
**Agent:** ref-search-agent
**Search Query:** Comprehensive reference research for Part 1: Core Foundation Infrastructure development
**Search Strategy:** Multi-source search across official SDK documentation, standards organizations, enterprise development patterns, and security frameworks

## Raw Reference Results

### 1. Claude Agents SDK Official Documentation

**Source:** Claude Agent SDK Overview Documentation
**URL:** https://docs.claude.com/en/api/agent-sdk/overview

**Key Features:**
- Built on Claude Code agent harness with production-ready building blocks
- Automatic context management and compaction to prevent context overflow
- Rich tool ecosystem: file operations, code execution, web search, MCP extensibility
- Advanced permissions with fine-grained control over agent capabilities
- Built-in error handling, session management, and monitoring
- Optimized Claude integration with automatic prompt caching

**Core Concepts:**
- **Authentication:** ANTHROPIC_API_KEY environment variable, support for Amazon Bedrock and Google Vertex AI
- **System Prompts:** Define agent role, expertise, and behavior
- **Tool Permissions:** allowedTools, disallowedTools, permissionMode
- **Model Context Protocol (MCP):** Extend agents with custom tools and integrations

**Installation Options:**
- TypeScript SDK: `npm install @anthropic-ai/claude-agent-sdk`
- Python SDK: Available for Python applications and data science
- Streaming vs Single Mode options for different use cases

### 2. Model Context Protocol (MCP) Documentation

**Source:** MCP Official Documentation
**URL:** https://docs.claude.com/en/docs/mcp

**Protocol Definition:**
- Open protocol standardizing how applications provide context to LLMs
- "USB-C port for AI applications" - standardized connection to data sources and tools
- Supports resource management, tool definitions, prompt templates, and connection setup

**MCP in SDK Configuration:**
**Source:** https://docs.claude.com/en/api/agent-sdk/mcp?codeTab=Python

**Configuration Options:**
```python
# Basic .mcp.json configuration
{
  "mcpServers": {
    "filesystem": {
      "command": "python",
      "args": ["-m", "mcp_server_filesystem"],
      "env": {
        "ALLOWED_PATHS": "/Users/me/projects"
      }
    }
  }
}
```

**Transport Types:**
- **stdio Servers:** External processes via stdin/stdout
- **HTTP/SSE Servers:** Remote servers with network communication
- **SDK MCP Servers:** In-process servers within application

**Authentication Methods:**
- Environment variables with Bearer tokens
- API key authentication
- OAuth2 (Note: OAuth2 MCP authentication in-client not currently supported)

**Error Handling:**
```python
# Check MCP server status
if message["type"] == "system" and message["subtype"] == "init":
    failed_servers = [s for s in message["mcp_servers"]
                     if s["status"] != "connected"]
```

### 3. WebSocket Standards and Implementation

**Source:** WebSocket Standards Tracker
**URL:** https://websocket.org/standards

**Core Specifications:**
- **RFC 6455:** The WebSocket Protocol (Internet Standard, December 2011)
- **RFC 7692:** Compression Extensions for permessage-deflate
- **RFC 8441:** HTTP/2 WebSockets using Extended CONNECT
- **RFC 9220:** HTTP/3 WebSockets over QUIC
- **W3C WebTransport:** Next-generation bidirectional communication protocol

**Browser Implementation Status:**
- **Basic WebSocket:** Chrome 16+, Firefox 11+, Safari 7+, Edge 12+
- **Compression (RFC 7692):** Chrome 32+, Firefox 37+, Safari 9+, Edge 12+
- **HTTP/2 WebSockets:** Chrome 91+, Edge 91+ (Firefox/Safari not supported)
- **WebTransport:** Chrome 97+, Edge 97+ (Firefox experimental, Safari not supported)

**Server Implementation:**
- **Nginx:** HTTP/1.1 WebSocket 1.3.13+, HTTP/2 WebSocket 1.25+, HTTP/3 experimental
- **Node.js:** All versions HTTP/1.1, HTTP/2 10.0+, HTTP/3 experimental
- **Python websockets:** 100% RFC 6455 compliance, 100% RFC 7692 compliance

**Feature Detection:**
```javascript
// Check WebSocket capabilities
const features = {
  basic: 'WebSocket' in window,
  secure: false,
  compression: false,
  http2: false,
  http3: false
};
```

### 4. Python Enterprise Development Standards

**Source:** Python Async Programming Documentation
**Source:** https://github.com/temporalio/documentation/blob/main/docs/develop/python/python-sdk-sync-vs-async.mdx

**Async Event Loop Best Practices:**
- Event loop runs in a single thread, executes all tasks sequentially
- Tasks only pass control when `await` keyword is executed
- **Critical Rule:** Never make blocking calls from async activities
- Use async-safe libraries (aiohttp, httpx) instead of synchronous ones (requests)

**Blocking Call Prevention:**
```python
# BAD - Blocks event loop
import requests
response = requests.get("https://api.example.com")  # Blocks entire event loop

# GOOD - Async-safe
import aiohttp
async with aiohttp.ClientSession() as session:
    async with session.get("https://api.example.com") as response:
        data = await response.json()
```

### 5. Testing Framework Standards

**Source:** pytest Good Integration Practices
**URL:** https://docs.pytest.org/en/stable/explanation/goodpractices.html

**Recommended Project Structure:**
```
pyproject.toml
src/
    mypkg/
        __init__.py
        app.py
        view.py
tests/
    test_app.py
    test_view.py
    ...
```

**Configuration Best Practices:**
```toml
[tool.pytest.ini_options]
addopts = [
    "--import-mode=importlib",
]
pythonpath = "src"
```

**Test Discovery:**
- Recursively searches for `test_*.py` or `*_test.py` files
- Collects `test` prefixed functions outside classes
- Collects `test` prefixed methods inside `Test` prefixed classes
- Supports unittest.TestCase subclassing

**Package Installation:**
```bash
pip install -e .  # Editable mode for development
```

### 6. API Design Standards (OpenAPI Specification)

**Source:** OpenAPI Specification (OAS)
**URL:** https://github.com/oai/openapi-specification/blob/main/README.md

**Specification Purpose:**
- Standard, programming language-agnostic interface description for HTTP APIs
- Enables humans and computers to discover and understand service capabilities
- Supports interactive documentation, code generation, and automation

**Key Features:**
- Language-independent API descriptions in YAML or JSON
- Supports REST API design patterns
- Facilitates both design-first and code-first development approaches
- Machine-readable definitions for automated tooling

**Use Cases:**
- Interactive documentation generation
- Client and server code generation
- Automated test case creation
- API discovery and integration

### 7. Microservices Architecture Patterns

**Source:** Microsoft Architecture Center - Microservices
**URL:** https://github.com/microsoftdocs/architecture-center/blob/main/docs/guide/architecture-styles/microservices.md

**Core Principles:**
- Small, independent, loosely coupled components
- Each service implements single business capability within bounded context
- Self-contained services with separate codebases and data stores
- Communication through well-defined APIs

**Essential Components:**
- **API Gateway:** Entry point for clients, handles cross-cutting concerns
- **Message-oriented Middleware:** Asynchronous communication (Kafka, Service Bus)
- **Observability:** Centralized logging, monitoring, distributed tracing
- **Data Management:** Polyglot persistence, service-owned data
- **Management/Orchestration:** Kubernetes, Azure Container Apps

**Best Practices:**
- Model services around business domain using DDD
- Decentralize everything (teams, design, building)
- Standardize technology choices (limited languages/frameworks)
- Private data storage for each service
- Well-designed APIs that model domain, not implementation
- Avoid coupling between services
- Use CI/CD pipelines for independent deployment

**Anti-patterns to Avoid:**
- Implementing microservices without business domain understanding
- Database entities as events
- Sharing common libraries between services
- Exposing microservices directly to consumers
- Generic events that force interpretation
- Configuration values inside microservices

### 8. Security and Authentication Standards

**Sources:** OAuth2 Implementation Guides, Microsoft Security Best Practices

**Authentication Patterns:**
- **OAuth2/OpenID Connect:** Industry standard for delegated authorization
- **mTLS (Mutual TLS):** Service-to-service encryption
- **API Keys:** Simple token-based authentication
- **Bearer Tokens:** JWT-based stateless authentication

**Security Best Practices:**
- Role-based access control (RBAC)
- API gateway policy enforcement
- Circuit breaker patterns for fault isolation
- Input validation and sanitization
- Secure communication protocols (HTTPS/WSS)
- Regular security audits and penetration testing

**Enterprise Security Considerations:**
- Zero-trust architecture principles
- Secrets management (environment variables, key vaults)
- Audit logging and monitoring
- Compliance with data protection regulations
- Regular security updates and patching

### 9. Performance Optimization Guidelines

**Sources:** Google Cloud Monitoring, Performance Best Practices

**Scalability Patterns:**
- **Horizontal scaling:** Load distribution across multiple instances
- **Caching strategies:** Redis, Memcached for frequently accessed data
- **Connection pooling:** Database and HTTP connection reuse
- **Async processing:** Non-blocking I/O operations

**Monitoring and Observability:**
- **Metrics collection:** Response times, error rates, throughput
- **Distributed tracing:** Request tracking across service boundaries
- **Application Performance Monitoring (APM):** Real-time performance insights
- **Log aggregation:** Centralized logging with correlation IDs

**Resource Management:**
- **Memory optimization:** Efficient data structures and garbage collection
- **CPU utilization:** Async/await patterns for non-blocking operations
- **Network optimization:** Compression, keep-alive connections
- **Database optimization:** Query optimization, connection pooling

### 10. Integration and Interoperability Standards

**API Design Standards:**
- **RESTful principles:** HTTP methods, status codes, resource-based URLs
- **Versioning strategies:** URL versioning, header versioning
- **Documentation standards:** OpenAPI/Swagger specifications
- **Error handling:** Consistent error response formats

**Integration Testing Frameworks:**
- **Contract testing:** Consumer-driven contract testing
- **End-to-end testing:** Complete workflow validation
- **Performance testing:** Load testing and benchmarking
- **Security testing:** Authentication and authorization validation

## Citation Information

### Primary Sources:
1. **Claude Agent SDK Documentation** - Anthropic, 2024
2. **Model Context Protocol Specification** - Model Context Protocol Initiative
3. **WebSocket RFC 6455** - IETF, December 2011
4. **OpenAPI Specification 3.0** - OpenAPI Initiative, Linux Foundation
5. **pytest Documentation** - pytest development team
6. **Microsoft Architecture Center** - Microsoft Corporation, 2025

### Secondary Sources:
1. **Temporalio Python Async Documentation** - Temporal Technologies
2. **Google Cloud Monitoring Documentation** - Google Cloud Platform
3. **WebSocket.org Standards Tracker** - Ably Realtime
4. **OAuth2 Implementation Guides** - Various open-source projects

## Source Documentation

**Access Methods:**
- All documentation accessed via official project websites and repositories
- OpenAPI specification available on GitHub under Apache 2.0 license
- WebSocket standards available via IETF RFC repository
- pytest documentation available at pytest.org

**Accessibility:**
- All sources are publicly accessible without authentication
- Documentation formats include HTML, Markdown, and PDF
- Source code repositories available on GitHub with appropriate licensing

## Reference Metadata

**Search Timestamp:** 2025-10-15 15:30:00
**Total Results:** 25+ documentation sources
**Quality Indicators:**
- Official vendor documentation (Claude, Google, Microsoft)
- Standards body specifications (IETF, OpenAPI Initiative)
- Open-source project documentation (pytest, WebSocket.org)
- Enterprise architecture patterns (Microsoft Architecture Center)

**Coverage Completeness:**
- ✅ SDK and framework documentation
- ✅ Protocol specifications (WebSocket, MCP)
- ✅ Development standards and best practices
- ✅ Security and authentication patterns
- ✅ Performance optimization guidelines
- ✅ Testing framework documentation
- ✅ API design standards
- ✅ Microservices architecture patterns

This comprehensive reference collection provides authoritative guidance for implementing Part 1: Core Foundation Infrastructure with enterprise-grade quality, security, and maintainability standards.