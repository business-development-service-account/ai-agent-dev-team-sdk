"""
CodeBase Analyzer - Specialized agent for code analysis.

Implements comprehensive code analysis with Serena MCP integration,
security scanning, performance analysis, and architecture review.
"""

import asyncio
import json
from typing import Dict, List, Optional, Any, Set
from datetime import datetime

from .base_agent import BaseAgent, TaskResult
from ..core.rules_engine import TaskSpec
from ..core.context_manager import AgentContext
from ..core.exceptions import TaskExecutionError, MCPServerError


class CodeBaseAnalyzer(BaseAgent):
    """
    Specialized agent for code analysis with Serena MCP integration.
    Handles code review, architecture analysis, and dependency mapping.
    """

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize CodeBaseAnalyzer."""
        super().__init__(agent_type="codebase_analyzer", config=config)
        self.max_files_to_analyze = self.config.get("max_files_to_analyze", 100)
        self.analysis_timeout = self.config.get("analysis_timeout", 600)

    async def _initialize_capabilities(self):
        """Initialize codebase analyzer capabilities."""
        # Security analysis capabilities
        self._add_capability(
            name="security_analysis",
            description="Comprehensive security vulnerability scanning",
            requires_mcp=True,
            mcp_server="serena",
            supported_task_types={"security_audit", "vulnerability_scan", "security_review"}
        )

        # Performance analysis capabilities
        self._add_capability(
            name="performance_analysis",
            description="Code performance analysis and bottleneck identification",
            requires_mcp=True,
            mcp_server="serena",
            supported_task_types={"performance_review", "optimization_analysis", "bottleneck_detection"}
        )

        # Architecture analysis capabilities
        self._add_capability(
            name="architecture_review",
            description="System architecture and design pattern analysis",
            requires_mcp=True,
            mcp_server="serena",
            supported_task_types={"architecture_analysis", "design_review", "pattern_analysis"}
        )

        # Code quality capabilities
        self._add_capability(
            name="code_quality_analysis",
            description="General code quality and maintainability analysis",
            supported_task_types={"code_review", "quality_assessment", "maintainability_analysis"}
        )

        # Task types specifically supported
        self.supported_task_types.update({
            "security_audit", "vulnerability_scan", "security_review",
            "performance_review", "optimization_analysis", "bottleneck_detection",
            "architecture_analysis", "design_review", "pattern_analysis",
            "code_review", "quality_assessment", "maintainability_analysis"
        })

    async def _execute_task_internal(
        self,
        task_spec: TaskSpec,
        context: Optional[AgentContext]
    ) -> TaskResult:
        """Execute code analysis task with Serena MCP integration."""
        task_start_time = datetime.utcnow()

        try:
            # Extract repository path from task metadata
            repository_path = task_spec.metadata.get("repository_path")
            if not repository_path:
                raise TaskExecutionError("Repository path not provided in task metadata")

            # Determine analysis type based on task type
            if task_spec.task_type in ["security_audit", "vulnerability_scan", "security_review"]:
                result = await self._execute_security_analysis(task_spec, repository_path, context)
            elif task_spec.task_type in ["performance_review", "optimization_analysis", "bottleneck_detection"]:
                result = await self._execute_performance_analysis(task_spec, repository_path, context)
            elif task_spec.task_type in ["architecture_analysis", "design_review", "pattern_analysis"]:
                result = await self._execute_architecture_analysis(task_spec, repository_path, context)
            else:
                result = await self._execute_code_quality_analysis(task_spec, repository_path, context)

            # Add execution metadata
            result.metadata.update({
                "repository_path": repository_path,
                "analysis_type": task_spec.task_type,
                "complexity_level": task_spec.complexity,
                "analysis_duration": (datetime.utcnow() - task_start_time).total_seconds(),
                "analyzer_version": "1.0.0"
            })

            return result

        except Exception as e:
            raise TaskExecutionError(f"Code analysis task execution failed: {e}") from e

    async def _execute_security_analysis(
        self,
        task_spec: TaskSpec,
        repository_path: str,
        context: Optional[AgentContext]
    ) -> TaskResult:
        """Execute security analysis using Serena MCP."""
        try:
            # Use Serena MCP for security analysis
            serena_result = await self._call_serena_analysis(
                repository_path=repository_path,
                analysis_type="security_focused",
                check_security=True,
                include_suggestions=True
            )

            # Build security-focused synthesis prompt
            synthesis_prompt = self._build_security_synthesis_prompt(
                repository_path,
                serena_result,
                task_spec.task_type
            )

            messages = [
                {
                    "role": "user",
                    "content": synthesis_prompt
                }
            ]

            system_prompt = context.system_prompt if context else await self._get_default_system_prompt()

            claude_response = await self._call_claude(messages, system_prompt)

            # Extract security metrics
            security_metrics = self._extract_security_metrics(serena_result)

            return self._create_task_result(
                task_id=task_spec.task_id,
                content=claude_response,
                confidence_score=0.90,
                sources=[repository_path],
                metadata={
                    "analysis_method": "serena_security",
                    "serena_data": serena_result,
                    "security_metrics": security_metrics,
                    "analysis_type": "security"
                }
            )

        except MCPServerError as e:
            # Fallback to local security analysis
            print(f"Serena MCP unavailable, using fallback security analysis: {e}")
            return await self._execute_fallback_security_analysis(task_spec, repository_path, context)

    async def _execute_performance_analysis(
        self,
        task_spec: TaskSpec,
        repository_path: str,
        context: Optional[AgentContext]
    ) -> TaskResult:
        """Execute performance analysis using Serena MCP."""
        try:
            # Use Serena MCP for performance analysis
            serena_result = await self._call_serena_analysis(
                repository_path=repository_path,
                analysis_type="performance",
                include_suggestions=True
            )

            # Build performance-focused synthesis prompt
            synthesis_prompt = self._build_performance_synthesis_prompt(
                repository_path,
                serena_result,
                task_spec.task_type
            )

            messages = [
                {
                    "role": "user",
                    "content": synthesis_prompt
                }
            ]

            system_prompt = context.system_prompt if context else await self._get_default_system_prompt()

            claude_response = await self._call_claude(messages, system_prompt)

            # Extract performance metrics
            performance_metrics = self._extract_performance_metrics(serena_result)

            return self._create_task_result(
                task_id=task_spec.task_id,
                content=claude_response,
                confidence_score=0.88,
                sources=[repository_path],
                metadata={
                    "analysis_method": "serena_performance",
                    "serena_data": serena_result,
                    "performance_metrics": performance_metrics,
                    "analysis_type": "performance"
                }
            )

        except MCPServerError as e:
            # Fallback to local performance analysis
            print(f"Serena MCP unavailable, using fallback performance analysis: {e}")
            return await self._execute_fallback_performance_analysis(task_spec, repository_path, context)

    async def _execute_architecture_analysis(
        self,
        task_spec: TaskSpec,
        repository_path: str,
        context: Optional[AgentContext]
    ) -> TaskResult:
        """Execute architecture analysis using Serena MCP."""
        try:
            # Use Serena MCP for architecture analysis
            serena_result = await self._call_serena_analysis(
                repository_path=repository_path,
                analysis_type="architecture",
                include_suggestions=True
            )

            # Build architecture-focused synthesis prompt
            synthesis_prompt = self._build_architecture_synthesis_prompt(
                repository_path,
                serena_result,
                task_spec.task_type
            )

            messages = [
                {
                    "role": "user",
                    "content": synthesis_prompt
                }
            ]

            system_prompt = context.system_prompt if context else await self._get_default_system_prompt()

            claude_response = await self._call_claude(messages, system_prompt)

            # Extract architecture metrics
            architecture_metrics = self._extract_architecture_metrics(serena_result)

            return self._create_task_result(
                task_id=task_spec.task_id,
                content=claude_response,
                confidence_score=0.85,
                sources=[repository_path],
                metadata={
                    "analysis_method": "serena_architecture",
                    "serena_data": serena_result,
                    "architecture_metrics": architecture_metrics,
                    "analysis_type": "architecture"
                }
            )

        except MCPServerError as e:
            # Fallback to local architecture analysis
            print(f"Serena MCP unavailable, using fallback architecture analysis: {e}")
            return await self._execute_fallback_architecture_analysis(task_spec, repository_path, context)

    async def _execute_code_quality_analysis(
        self,
        task_spec: TaskSpec,
        repository_path: str,
        context: Optional[AgentContext]
    ) -> TaskResult:
        """Execute general code quality analysis."""
        # Build code quality analysis prompt
        analysis_prompt = self._build_code_quality_prompt(
            repository_path,
            task_spec.task_type
        )

        messages = [
            {
                "role": "user",
                "content": analysis_prompt
            }
        ]

        system_prompt = context.system_prompt if context else await self._get_default_system_prompt()

        claude_response = await self._call_claude(messages, system_prompt)

        # Generate quality metrics
        quality_metrics = self._generate_quality_metrics(repository_path)

        return self._create_task_result(
            task_id=task_spec.task_id,
            content=claude_response,
            confidence_score=0.80,
            sources=[repository_path],
            metadata={
                "analysis_method": "claude_quality",
                "quality_metrics": quality_metrics,
                "analysis_type": "quality",
                "fallback_used": True
            }
        )

    async def _call_serena_analysis(
        self,
        repository_path: str,
        analysis_type: str,
        check_security: bool = False,
        include_suggestions: bool = True
    ) -> Dict[str, Any]:
        """Call Serena MCP server for code analysis."""
        params = {
            "repository_path": repository_path,
            "analysis_type": analysis_type,
            "include_suggestions": include_suggestions,
            "check_security": check_security,
            "file_patterns": ["**/*.py", "**/*.js", "**/*.ts", "**/*.java"],
            "exclude_patterns": ["**/test/**", "**/node_modules/**", "**/.git/**"]
        }

        return await self._call_mcp_server("serena", "analyze_code", params)

    def _build_security_synthesis_prompt(
        self,
        repository_path: str,
        serena_data: Dict[str, Any],
        analysis_type: str
    ) -> str:
        """Build security-focused synthesis prompt."""
        return f"""
Based on the following security analysis data from Serena, provide a comprehensive {analysis_type} for repository: {repository_path}

Security Analysis Data:
{json.dumps(serena_data, indent=2)}

Please provide a detailed security analysis including:
1. Executive summary of security posture
2. Critical and high-severity vulnerabilities
3. Medium and low-priority security issues
4. Recommended remediation actions prioritized by risk
5. Security best practices implementation suggestions
6. Compliance considerations (if applicable)
7. Security monitoring recommendations

Focus on providing actionable, specific recommendations with clear risk assessments.
"""

    def _build_performance_synthesis_prompt(
        self,
        repository_path: str,
        serena_data: Dict[str, Any],
        analysis_type: str
    ) -> str:
        """Build performance-focused synthesis prompt."""
        return f"""
Based on the following performance analysis data from Serena, provide a comprehensive {analysis_type} for repository: {repository_path}

Performance Analysis Data:
{json.dumps(serena_data, indent=2)}

Please provide a detailed performance analysis including:
1. Performance bottlenecks and hotspots
2. Resource usage patterns and inefficiencies
3. Algorithmic complexity issues
4. Database and I/O optimization opportunities
5. Memory usage optimization suggestions
6. Concurrency and threading considerations
7. Scalability recommendations

Focus on providing specific, actionable recommendations with potential performance improvements.
"""

    def _build_architecture_synthesis_prompt(
        self,
        repository_path: str,
        serena_data: Dict[str, Any],
        analysis_type: str
    ) -> str:
        """Build architecture-focused synthesis prompt."""
        return f"""
Based on the following architecture analysis data from Serena, provide a comprehensive {analysis_type} for repository: {repository_path}

Architecture Analysis Data:
{json.dumps(serena_data, indent=2)}

Please provide a detailed architecture analysis including:
1. System architecture overview and patterns
2. Design pattern identification and assessment
3. Module coupling and cohesion analysis
4. Layer separation and responsibility boundaries
5. Extensibility and maintainability assessment
6. Architectural debt and technical risks
7. Refactoring and improvement recommendations

Focus on providing architectural insights with specific, implementable recommendations.
"""

    def _build_code_quality_prompt(
        self,
        repository_path: str,
        analysis_type: str
    ) -> str:
        """Build code quality analysis prompt."""
        return f"""
Perform a comprehensive {analysis_type} for the repository at: {repository_path}

Please analyze the codebase and provide:
1. Overall code quality assessment
2. Maintainability and readability evaluation
3. Code complexity analysis
4. Duplication and redundancy identification
5. Testing coverage and quality
6. Documentation adequacy
7. Best practices adherence
8. Specific improvement recommendations

Since direct repository access is not available, focus on general code quality principles and provide template-based recommendations that would apply to typical codebases of this type.
"""

    def _extract_security_metrics(self, serena_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract security metrics from Serena analysis data."""
        metrics = {
            "total_vulnerabilities": 0,
            "critical_count": 0,
            "high_count": 0,
            "medium_count": 0,
            "low_count": 0,
            "security_score": 0.0
        }

        if "findings" in serena_data and "security" in serena_data["findings"]:
            security_findings = serena_data["findings"]["security"]
            if "vulnerabilities" in security_findings:
                for vuln in security_findings["vulnerabilities"]:
                    severity = vuln.get("severity", "low").lower()
                    metrics["total_vulnerabilities"] += 1

                    if severity == "critical":
                        metrics["critical_count"] += 1
                    elif severity == "high":
                        metrics["high_count"] += 1
                    elif severity == "medium":
                        metrics["medium_count"] += 1
                    else:
                        metrics["low_count"] += 1

            if "security_score" in security_findings:
                metrics["security_score"] = security_findings["security_score"]

        return metrics

    def _extract_performance_metrics(self, serena_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract performance metrics from Serena analysis data."""
        metrics = {
            "total_bottlenecks": 0,
            "performance_score": 0.0,
            "complexity_score": 0.0
        }

        if "findings" in serena_data and "performance" in serena_data["findings"]:
            perf_findings = serena_data["findings"]["performance"]

            if "bottlenecks" in perf_findings:
                metrics["total_bottlenecks"] = len(perf_findings["bottlenecks"])

            if "performance_score" in perf_findings:
                metrics["performance_score"] = perf_findings["performance_score"]

            if "complexity_score" in perf_findings:
                metrics["complexity_score"] = perf_findings["complexity_score"]

        return metrics

    def _extract_architecture_metrics(self, serena_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract architecture metrics from Serena analysis data."""
        metrics = {
            "architecture_score": 0.0,
            "design_patterns_found": [],
            "coupling_score": 0.0,
            "cohesion_score": 0.0
        }

        if "findings" in serena_data and "architecture" in serena_data["findings"]:
            arch_findings = serena_data["findings"]["architecture"]

            if "architecture_score" in arch_findings:
                metrics["architecture_score"] = arch_findings["architecture_score"]

            if "patterns" in arch_findings:
                metrics["design_patterns_found"] = [
                    pattern.get("pattern", "unknown")
                    for pattern in arch_findings["patterns"]
                ]

            if "coupling_score" in arch_findings:
                metrics["coupling_score"] = arch_findings["coupling_score"]

            if "cohesion_score" in arch_findings:
                metrics["cohesion_score"] = arch_findings["cohesion_score"]

        return metrics

    def _generate_quality_metrics(self, repository_path: str) -> Dict[str, Any]:
        """Generate placeholder quality metrics for fallback analysis."""
        return {
            "maintainability_score": 0.75,
            "readability_score": 0.80,
            "complexity_score": 0.70,
            "documentation_score": 0.60,
            "testing_score": 0.65,
            "overall_quality_score": 0.70
        }

    async def _execute_fallback_security_analysis(
        self,
        task_spec: TaskSpec,
        repository_path: str,
        context: Optional[AgentContext]
    ) -> TaskResult:
        """Execute fallback security analysis without MCP."""
        analysis_prompt = f"""
Perform a security vulnerability assessment for the repository: {repository_path}

Since direct analysis tools are unavailable, provide:
1. Common security vulnerabilities to check for in this type of codebase
2. Security best practices that should be implemented
3. Potential security risks based on the repository structure
4. Recommended security scanning tools and techniques
5. Security monitoring and logging recommendations

Focus on providing actionable security guidance that can be applied to improve the security posture.
"""

        messages = [{"role": "user", "content": analysis_prompt}]
        system_prompt = context.system_prompt if context else await self._get_default_system_prompt()

        claude_response = await self._call_claude(messages, system_prompt)

        return self._create_task_result(
            task_id=task_spec.task_id,
            content=claude_response,
            confidence_score=0.70,
            sources=[repository_path],
            metadata={
                "analysis_method": "fallback_security",
                "analysis_type": "security",
                "fallback_used": True
            }
        )

    async def _execute_fallback_performance_analysis(
        self,
        task_spec: TaskSpec,
        repository_path: str,
        context: Optional[AgentContext]
    ) -> TaskResult:
        """Execute fallback performance analysis without MCP."""
        analysis_prompt = f"""
Perform a performance analysis assessment for the repository: {repository_path}

Since direct analysis tools are unavailable, provide:
1. Common performance bottlenecks in this type of application
2. Performance optimization strategies and techniques
3. Tools and methodologies for performance profiling
4. Scalability considerations and recommendations
5. Database and I/O optimization opportunities
6. Caching strategies and implementation patterns

Focus on providing actionable performance guidance that can improve application performance.
"""

        messages = [{"role": "user", "content": analysis_prompt}]
        system_prompt = context.system_prompt if context else await self._get_default_system_prompt()

        claude_response = await self._call_claude(messages, system_prompt)

        return self._create_task_result(
            task_id=task_spec.task_id,
            content=claude_response,
            confidence_score=0.68,
            sources=[repository_path],
            metadata={
                "analysis_method": "fallback_performance",
                "analysis_type": "performance",
                "fallback_used": True
            }
        )

    async def _execute_fallback_architecture_analysis(
        self,
        task_spec: TaskSpec,
        repository_path: str,
        context: Optional[AgentContext]
    ) -> TaskResult:
        """Execute fallback architecture analysis without MCP."""
        analysis_prompt = f"""
Perform an architecture analysis for the repository: {repository_path}

Since direct analysis tools are unavailable, provide:
1. Common architectural patterns for this type of application
2. Design principles and best practices to follow
3. Potential architectural improvements and refactoring opportunities
4. Modularity and separation of concerns recommendations
5. Extensibility and maintainability considerations
6. Integration patterns and architectural decision frameworks

Focus on providing actionable architectural guidance that can improve system design.
"""

        messages = [{"role": "user", "content": analysis_prompt}]
        system_prompt = context.system_prompt if context else await self._get_default_system_prompt()

        claude_response = await self._call_claude(messages, system_prompt)

        return self._create_task_result(
            task_id=task_spec.task_id,
            content=claude_response,
            confidence_score=0.65,
            sources=[repository_path],
            metadata={
                "analysis_method": "fallback_architecture",
                "analysis_type": "architecture",
                "fallback_used": True
            }
        )

    async def _get_default_system_prompt(self) -> str:
        """Get default system prompt for codebase analyzer."""
        return """You are a specialized codebase analyzer focused on comprehensive code analysis and intelligence. Your expertise includes:

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

## Current Task
Focus on thorough code analysis with detailed findings and actionable recommendations."""