"""
BackEnd Coder - Specialized agent for backend development.

Implements robust, scalable server-side application development with
API design, database integration, and security best practices.
"""

import json
from typing import Dict, List, Optional, Any, Set
from datetime import datetime

from .base_agent import BaseAgent, TaskResult
from ..core.rules_engine import TaskSpec
from ..core.context_manager import AgentContext
from ..core.exceptions import TaskExecutionError


class BackEndCoder(BaseAgent):
    """
    Specialized backend developer focused on creating robust, scalable
    server-side applications with proper security and performance.
    """

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize BackEndCoder."""
        super().__init__(agent_type="backend", config=config)
        self.framework_preference = self.config.get("framework", "fastapi")
        self.database_preference = self.config.get("database", "postgresql")

    async def _initialize_capabilities(self):
        """Initialize backend coder capabilities."""
        # API Development capabilities
        self._add_capability(
            name="api_development",
            description="RESTful API design and implementation",
            supported_task_types={
                "api_development", "endpoint_design", "api_integration"
            }
        )

        # Database Design capabilities
        self._add_capability(
            name="database_design",
            description="Database schema design and optimization",
            supported_task_types={
                "database_design", "schema_migration", "query_optimization"
            }
        )

        # Security Implementation capabilities
        self._add_capability(
            name="security_implementation",
            description="Authentication, authorization, and data protection",
            supported_task_types={
                "authentication", "authorization", "security_audit"
            }
        )

        # Microservices Architecture capabilities
        self._add_capability(
            name="microservices",
            description="Microservices architecture and integration",
            supported_task_types={
                "microservices_design", "service_integration", "api_gateway"
            }
        )

        # Task types specifically supported
        self.supported_task_types.update({
            "api_development", "endpoint_design", "api_integration",
            "database_design", "schema_migration", "query_optimization",
            "authentication", "authorization", "security_audit",
            "microservices_design", "service_integration", "api_gateway",
            "data_validation", "error_handling", "logging_monitoring",
            "caching_strategy", "performance_optimization"
        })

    async def _execute_task_internal(
        self,
        task_spec: TaskSpec,
        context: Optional[AgentContext]
    ) -> TaskResult:
        """Execute backend development task."""
        task_start_time = datetime.utcnow()

        try:
            # Extract backend-specific parameters
            api_spec = task_spec.metadata.get("api_spec", {})
            database_spec = task_spec.metadata.get("database_spec", {})
            security_spec = task_spec.metadata.get("security_spec", {})
            framework = task_spec.metadata.get("framework", self.framework_preference)
            database = task_spec.metadata.get("database", self.database_preference)

            # Determine task type and execute accordingly
            if task_spec.task_type in ["api_development", "endpoint_design", "api_integration"]:
                result = await self._execute_api_development(
                    task_spec, api_spec, framework, context
                )
            elif task_spec.task_type in ["database_design", "schema_migration", "query_optimization"]:
                result = await self._execute_database_development(
                    task_spec, database_spec, database, context
                )
            elif task_spec.task_type in ["authentication", "authorization", "security_audit"]:
                result = await self._execute_security_implementation(
                    task_spec, security_spec, framework, context
                )
            elif task_spec.task_type in ["microservices_design", "service_integration", "api_gateway"]:
                result = await self._execute_microservices_development(
                    task_spec, api_spec, framework, context
                )
            else:
                result = await self._execute_general_backend_task(
                    task_spec, framework, context
                )

            # Add execution metadata
            result.metadata.update({
                "framework": framework,
                "database": database,
                "complexity_level": task_spec.complexity,
                "development_duration": (datetime.utcnow() - task_start_time).total_seconds(),
                "backend_version": "1.0.0"
            })

            return result

        except Exception as e:
            raise TaskExecutionError(f"Backend development task failed: {e}") from e

    async def _execute_api_development(
        self,
        task_spec: TaskSpec,
        api_spec: Dict[str, Any],
        framework: str,
        context: Optional[AgentContext]
    ) -> TaskResult:
        """Execute API development task."""
        # Build API development prompt
        api_prompt = self._build_api_development_prompt(
            task_spec.task,
            api_spec,
            framework
        )

        messages = [{"role": "user", "content": api_prompt}]
        system_prompt = context.system_prompt if context else await self._get_default_system_prompt()

        claude_response = await self._call_claude(messages, system_prompt)

        # Generate API metadata
        api_metadata = {
            "framework": framework,
            "endpoints": api_spec.get("endpoints", []),
            "authentication": api_spec.get("authentication", "jwt"),
            "validation": api_spec.get("validation", True),
            "documentation": "openapi_3_0"
        }

        return self._create_task_result(
            task_id=task_spec.task_id,
            content=claude_response,
            confidence_score=0.87,
            sources=[],
            metadata={
                "development_method": "claude_api",
                "api_metadata": api_metadata,
                "task_type": "api_development"
            }
        )

    async def _execute_database_development(
        self,
        task_spec: TaskSpec,
        database_spec: Dict[str, Any],
        database: str,
        context: Optional[AgentContext]
    ) -> TaskResult:
        """Execute database development task."""
        # Build database development prompt
        db_prompt = self._build_database_development_prompt(
            task_spec.task,
            database_spec,
            database
        )

        messages = [{"role": "user", "content": db_prompt}]
        system_prompt = context.system_prompt if context else await self._get_default_system_prompt()

        claude_response = await self._call_claude(messages, system_prompt)

        # Generate database metadata
        db_metadata = {
            "database_type": database,
            "tables": database_spec.get("tables", []),
            "relationships": database_spec.get("relationships", []),
            "indexes": database_spec.get("indexes", []),
            "migrations": True
        }

        return self._create_task_result(
            task_id=task_spec.task_id,
            content=claude_response,
            confidence_score=0.85,
            sources=[],
            metadata={
                "development_method": "claude_database",
                "database_metadata": db_metadata,
                "task_type": "database_development"
            }
        )

    async def _execute_security_implementation(
        self,
        task_spec: TaskSpec,
        security_spec: Dict[str, Any],
        framework: str,
        context: Optional[AgentContext]
    ) -> TaskResult:
        """Execute security implementation task."""
        # Build security implementation prompt
        security_prompt = self._build_security_implementation_prompt(
            task_spec.task,
            security_spec,
            framework
        )

        messages = [{"role": "user", "content": security_prompt}]
        system_prompt = context.system_prompt if context else await self._get_default_system_prompt()

        claude_response = await self._call_claude(messages, system_prompt)

        # Generate security metadata
        security_metadata = {
            "authentication_method": security_spec.get("authentication", "jwt"),
            "authorization_model": security_spec.get("authorization", "rbac"),
            "encryption": security_spec.get("encryption", "aes256"),
            "compliance": security_spec.get("compliance", ["gdpr", "ccpa"])
        }

        return self._create_task_result(
            task_id=task_spec.task_id,
            content=claude_response,
            confidence_score=0.90,
            sources=[],
            metadata={
                "development_method": "claude_security",
                "security_metadata": security_metadata,
                "task_type": "security_implementation"
            }
        )

    async def _execute_microservices_development(
        self,
        task_spec: TaskSpec,
        api_spec: Dict[str, Any],
        framework: str,
        context: Optional[AgentContext]
    ) -> TaskResult:
        """Execute microservices development task."""
        # Build microservices development prompt
        microservices_prompt = self._build_microservices_development_prompt(
            task_spec.task,
            api_spec,
            framework
        )

        messages = [{"role": "user", "content": microservices_prompt}]
        system_prompt = context.system_prompt if context else await self._get_default_system_prompt()

        claude_response = await self._call_claude(messages, system_prompt)

        # Generate microservices metadata
        microservices_metadata = {
            "architecture_pattern": api_spec.get("pattern", "api_gateway"),
            "services": api_spec.get("services", []),
            "communication": api_spec.get("communication", "rest_api"),
            "discovery": api_spec.get("discovery", "service_registry")
        }

        return self._create_task_result(
            task_id=task_spec.task_id,
            content=claude_response,
            confidence_score=0.83,
            sources=[],
            metadata={
                "development_method": "claude_microservices",
                "microservices_metadata": microservices_metadata,
                "task_type": "microservices_development"
            }
        )

    async def _execute_general_backend_task(
        self,
        task_spec: TaskSpec,
        framework: str,
        context: Optional[AgentContext]
    ) -> TaskResult:
        """Execute general backend development task."""
        # Build general backend prompt
        general_prompt = self._build_general_backend_prompt(task_spec.task, framework)

        messages = [{"role": "user", "content": general_prompt}]
        system_prompt = context.system_prompt if context else await self._get_default_system_prompt()

        claude_response = await self._call_claude(messages, system_prompt)

        return self._create_task_result(
            task_id=task_spec.task_id,
            content=claude_response,
            confidence_score=0.80,
            sources=[],
            metadata={
                "development_method": "claude_general",
                "task_type": "general_backend"
            }
        )

    def _build_api_development_prompt(
        self,
        task_description: str,
        api_spec: Dict[str, Any],
        framework: str
    ) -> str:
        """Build API development prompt."""
        api_info = json.dumps(api_spec, indent=2)

        return f"""
Develop a robust, scalable RESTful API using {framework} for the following requirements:

Task Description: {task_description}

API Specification:
{api_info}

Please provide:
1. Complete API implementation with proper routing
2. Request/response data models and validation
3. Error handling and status code management
4. Authentication and authorization middleware
5. Input validation and sanitization
6. API documentation (OpenAPI/Swagger)
7. Rate limiting and throttling implementation
8. Logging and monitoring setup
9. Unit and integration test examples
10. Deployment configuration

Requirements:
- Follow RESTful API best practices
- Implement proper HTTP status codes
- Use semantic versioning
- Ensure security best practices
- Include comprehensive error handling
- Optimize for performance and scalability
- Provide clear API documentation
"""

    def _build_database_development_prompt(
        self,
        task_description: str,
        database_spec: Dict[str, Any],
        database: str
    ) -> str:
        """Build database development prompt."""
        db_info = json.dumps(database_spec, indent=2)

        return f"""
Design and implement a robust database schema using {database} for the following requirements:

Task Description: {task_description}

Database Specification:
{db_info}

Please provide:
1. Complete database schema with proper normalization
2. Table relationships and foreign key constraints
3. Indexes for optimal query performance
4. Database migration scripts
5. Seed data and fixtures
6. Query optimization techniques
7. Backup and recovery strategies
8. Security considerations (SQL injection protection)
9. Connection pooling and scaling
10. Data validation and constraints

Requirements:
- Follow database normalization principles
- Optimize for query performance
- Ensure data integrity and consistency
- Implement proper security measures
- Design for scalability and maintainability
- Include comprehensive error handling
"""

    def _build_security_implementation_prompt(
        self,
        task_description: str,
        security_spec: Dict[str, Any],
        framework: str
    ) -> str:
        """Build security implementation prompt."""
        security_info = json.dumps(security_spec, indent=2)

        return f"""
Implement comprehensive security measures for the following {framework} application:

Task Description: {task_description}

Security Specification:
{security_info}

Please provide:
1. Authentication system implementation (JWT/OAuth2)
2. Authorization and role-based access control (RBAC)
3. Input validation and sanitization middleware
4. SQL injection and XSS prevention
5. CORS configuration and security headers
6. Session management and security
7. API rate limiting and throttling
8. Encryption for sensitive data (at rest and in transit)
9. Security logging and monitoring
10. Compliance measures (GDPR, CCPA, etc.)

Requirements:
- Follow security best practices and OWASP guidelines
- Implement defense-in-depth security strategy
- Ensure proper authentication and authorization
- Protect against common web vulnerabilities
- Implement proper data encryption
- Include comprehensive security logging
- Ensure compliance with privacy regulations
"""

    def _build_microservices_development_prompt(
        self,
        task_description: str,
        microservices_spec: Dict[str, Any],
        framework: str
    ) -> str:
        """Build microservices development prompt."""
        microservices_info = json.dumps(microservices_spec, indent=2)

        return f"""
Design and implement a microservices architecture using {framework} for the following requirements:

Task Description: {task_description}

Microservices Specification:
{microservices_info}

Please provide:
1. Service decomposition and domain boundaries
2. API gateway and service discovery implementation
3. Inter-service communication patterns (REST, gRPC, messaging)
4. Data consistency and distributed transactions
5. Circuit breaker and fault tolerance patterns
6. Service monitoring and health checks
7. Centralized logging and tracing
8. Configuration management
9. Containerization and deployment strategies
10. Database per service vs shared database decisions

Requirements:
- Follow microservices best practices
- Ensure loose coupling and high cohesion
- Implement proper fault tolerance
- Design for scalability and maintainability
- Include comprehensive monitoring
- Consider data consistency implications
- Plan for deployment and operations
"""

    def _build_general_backend_prompt(self, task_description: str, framework: str) -> str:
        """Build general backend development prompt."""
        return f"""
Implement a robust backend solution using {framework} for the following requirement:

Task Description: {task_description}

Please provide:
1. Complete backend implementation
2. Proper project structure and organization
3. Database integration and data models
4. API endpoints and business logic
5. Error handling and validation
6. Authentication and authorization
7. Logging and monitoring setup
8. Testing strategy and examples
9. Configuration management
10. Deployment and operational considerations

Requirements:
- Use modern backend development practices
- Ensure security best practices
- Implement proper error handling
- Optimize for performance and scalability
- Include comprehensive testing
- Provide clear documentation
- Consider deployment and operations
"""

    async def _get_default_system_prompt(self) -> str:
        """Get default system prompt for backend coder."""
        return """You are a specialized backend developer focused on creating robust, scalable server-side applications. Your expertise includes:

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
Focus on creating robust, secure, and scalable backend APIs with proper testing and documentation."""