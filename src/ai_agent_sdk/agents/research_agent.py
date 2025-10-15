"""
Research Agent - Specialized agent for research tasks.

Implements comprehensive research capabilities with Perplexity MCP integration,
knowledge synthesis, and competitive analysis.
"""

import asyncio
import json
from typing import Dict, List, Optional, Any, Set
from datetime import datetime

from .base_agent import BaseAgent, TaskResult
from ..core.rules_engine import TaskSpec
from ..core.context_manager import AgentContext
from ..core.exceptions import TaskExecutionError, MCPServerError


class ResearchAgent(BaseAgent):
    """
    Specialized agent for research tasks with Perplexity MCP integration.
    Handles web research, knowledge synthesis, and competitive analysis.
    """

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize ResearchAgent."""
        super().__init__(agent_type="research", config=config)
        self.max_sources = self.config.get("max_sources", 20)
        self.research_timeout = self.config.get("research_timeout", 300)

    async def _initialize_capabilities(self):
        """Initialize research agent capabilities."""
        # Core research capabilities
        self._add_capability(
            name="web_research",
            description="Comprehensive web research using search engines",
            supported_task_types={"market_research", "competitive_analysis", "technology_research"}
        )

        self._add_capability(
            name="knowledge_synthesis",
            description="Synthesize information from multiple sources",
            supported_task_types={"research_synthesis", "knowledge_compilation"}
        )

        self._add_capability(
            name="competitive_analysis",
            description="Analyze competitive landscape and market position",
            requires_mcp=True,
            mcp_server="perplexity",
            supported_task_types={"competitive_research", "market_analysis"}
        )

        self._add_capability(
            name="source_verification",
            description="Verify and validate source credibility",
            supported_task_types={"fact_checking", "source_validation"}
        )

        # Task types specifically supported
        self.supported_task_types.update({
            "market_research", "competitive_research", "technology_research",
            "academic_research", "industry_analysis", "trend_analysis",
            "knowledge_synthesis", "source_verification"
        })

    async def _execute_task_internal(
        self,
        task_spec: TaskSpec,
        context: Optional[AgentContext]
    ) -> TaskResult:
        """Execute research task with Perplexity MCP integration."""
        task_start_time = datetime.utcnow()

        try:
            # Determine research approach based on task type
            if task_spec.task_type in ["competitive_research", "market_analysis"]:
                result = await self._execute_competitive_research(task_spec, context)
            elif task_spec.task_type in ["technology_research", "academic_research"]:
                result = await self._execute_technology_research(task_spec, context)
            elif task_spec.task_type in ["knowledge_synthesis", "research_synthesis"]:
                result = await self._execute_knowledge_synthesis(task_spec, context)
            else:
                result = await self._execute_general_research(task_spec, context)

            # Add execution metadata
            result.metadata.update({
                "research_method": result.metadata.get("research_method", "general"),
                "sources_count": len(result.sources),
                "complexity_level": task_spec.complexity,
                "research_duration": (datetime.utcnow() - task_start_time).total_seconds()
            })

            return result

        except Exception as e:
            raise TaskExecutionError(f"Research task execution failed: {e}") from e

    async def _execute_competitive_research(
        self,
        task_spec: TaskSpec,
        context: Optional[AgentContext]
    ) -> TaskResult:
        """Execute competitive research using Perplexity MCP."""
        try:
            # Try Perplexity MCP first
            perplexity_result = await self._call_perplexity_research(
                query=task_spec.task,
                complexity_level=self._map_complexity_level(task_spec.complexity),
                research_mode="competitive"
            )

            # Synthesize findings with Claude
            synthesis_prompt = self._build_synthesis_prompt(
                task_spec.task,
                perplexity_result,
                "competitive_analysis"
            )

            messages = [
                {
                    "role": "user",
                    "content": synthesis_prompt
                }
            ]

            system_prompt = context.system_prompt if context else await self._get_default_system_prompt()

            claude_response = await self._call_claude(messages, system_prompt)

            # Extract sources from Perplexity result
            sources = self._extract_sources_from_perplexity(perplexity_result)

            return self._create_task_result(
                task_id=task_spec.task_id,
                content=claude_response,
                confidence_score=0.85,
                sources=sources,
                metadata={
                    "research_method": "perplexity_mcp",
                    "perplexity_data": perplexity_result,
                    "analysis_type": "competitive"
                }
            )

        except MCPServerError as e:
            # Fallback to general research
            print(f"Perplexity MCP unavailable, using fallback research: {e}")
            return await self._execute_general_research(task_spec, context)

    async def _execute_technology_research(
        self,
        task_spec: TaskSpec,
        context: Optional[AgentContext]
    ) -> TaskResult:
        """Execute technology research with comprehensive analysis."""
        try:
            # Use Perplexity for technology research
            perplexity_result = await self._call_perplexity_research(
                query=task_spec.task,
                complexity_level=self._map_complexity_level(task_spec.complexity),
                research_mode="technical"
            )

            # Build technology-focused synthesis prompt
            synthesis_prompt = self._build_technology_synthesis_prompt(
                task_spec.task,
                perplexity_result
            )

            messages = [
                {
                    "role": "user",
                    "content": synthesis_prompt
                }
            ]

            system_prompt = context.system_prompt if context else await self._get_default_system_prompt()

            claude_response = await self._call_claude(messages, system_prompt)

            # Extract sources
            sources = self._extract_sources_from_perplexity(perplexity_result)

            return self._create_task_result(
                task_id=task_spec.task_id,
                content=claude_response,
                confidence_score=0.87,
                sources=sources,
                metadata={
                    "research_method": "perplexity_technical",
                    "perplexity_data": perplexity_result,
                    "analysis_type": "technology"
                }
            )

        except MCPServerError as e:
            # Fallback to general research
            print(f"Perplexity MCP unavailable, using fallback research: {e}")
            return await self._execute_general_research(task_spec, context)

    async def _execute_knowledge_synthesis(
        self,
        task_spec: TaskSpec,
        context: Optional[AgentContext]
    ) -> TaskResult:
        """Execute knowledge synthesis from multiple sources."""
        # Break down the task into research queries
        research_queries = self._generate_research_queries(task_spec.task)

        all_sources = []
        research_data = []

        # Execute research queries
        for query in research_queries:
            try:
                result = await self._call_perplexity_research(
                    query=query,
                    complexity_level="medium",
                    research_mode="comprehensive"
                )
                research_data.append(result)
                all_sources.extend(self._extract_sources_from_perplexity(result))

            except MCPServerError:
                # Skip this query if Perplexity is unavailable
                continue

        # Synthesize all research data
        synthesis_prompt = self._build_knowledge_synthesis_prompt(
            task_spec.task,
            research_data
        )

        messages = [
            {
                "role": "user",
                "content": synthesis_prompt
            }
        ]

        system_prompt = context.system_prompt if context else await self._get_default_system_prompt()

        claude_response = await self._call_claude(messages, system_prompt)

        # Remove duplicate sources
        unique_sources = list(set(all_sources))

        return self._create_task_result(
            task_id=task_spec.task_id,
            content=claude_response,
            confidence_score=0.90,
            sources=unique_sources,
            metadata={
                "research_method": "knowledge_synthesis",
                "queries_executed": len(research_queries),
                "sources_count": len(unique_sources),
                "analysis_type": "synthesis"
            }
        )

    async def _execute_general_research(
        self,
        task_spec: TaskSpec,
        context: Optional[AgentContext]
    ) -> TaskResult:
        """Execute general research without MCP dependencies."""
        # Build research prompt for Claude
        research_prompt = self._build_general_research_prompt(task_spec.task)

        messages = [
            {
                "role": "user",
                "content": research_prompt
            }
        ]

        system_prompt = context.system_prompt if context else await self._get_default_system_prompt()

        claude_response = await self._call_claude(messages, system_prompt)

        # Generate synthetic sources for fallback
        sources = self._generate_fallback_sources(task_spec.task)

        return self._create_task_result(
            task_id=task_spec.task_id,
            content=claude_response,
            confidence_score=0.75,  # Lower confidence without MCP
            sources=sources,
            metadata={
                "research_method": "claude_only",
                "analysis_type": "general",
                "fallback_used": True
            }
        )

    async def _call_perplexity_research(
        self,
        query: str,
        complexity_level: str = "medium",
        research_mode: str = "comprehensive"
    ) -> Dict[str, Any]:
        """Call Perplexity MCP server for research."""
        params = {
            "query": query,
            "complexity_level": complexity_level,
            "research_mode": research_mode,
            "max_sources": self.max_sources,
            "include_analysis": True
        }

        return await self._call_mcp_server("perplexity", "research", params)

    def _map_complexity_level(self, complexity: int) -> str:
        """Map task complexity to Perplexity complexity level."""
        if complexity <= 3:
            return "low"
        elif complexity <= 7:
            return "medium"
        else:
            return "high"

    def _build_synthesis_prompt(
        self,
        original_query: str,
        perplexity_data: Dict[str, Any],
        analysis_type: str
    ) -> str:
        """Build synthesis prompt for Claude."""
        return f"""
Based on the following research data, provide a comprehensive {analysis_type} for the query: "{original_query}"

Research Data:
{json.dumps(perplexity_data, indent=2)}

Please synthesize this information into:
1. Key findings and insights
2. Actionable recommendations
3. Important trends and patterns
4. Risk factors and considerations
5. Next steps for further investigation

Ensure your response is well-structured, data-driven, and provides specific, actionable insights.
"""

    def _build_technology_synthesis_prompt(
        self,
        original_query: str,
        perplexity_data: Dict[str, Any]
    ) -> str:
        """Build technology-focused synthesis prompt."""
        return f"""
Analyze the following technology research data for the query: "{original_query}"

Research Data:
{json.dumps(perplexity_data, indent=2)}

Provide a comprehensive technology analysis including:
1. Technology landscape overview
2. Key players and solutions
3. Technical trends and innovations
4. Implementation considerations
5. Competitive advantages and disadvantages
6. Recommendations for adoption or further investigation

Focus on technical accuracy, practical insights, and actionable recommendations.
"""

    def _build_knowledge_synthesis_prompt(
        self,
        original_query: str,
        research_data: List[Dict[str, Any]]
    ) -> str:
        """Build knowledge synthesis prompt."""
        combined_data = {
            "query": original_query,
            "research_results": research_data
        }

        return f"""
Synthesize the following multiple research sources to provide comprehensive insights for: "{original_query}"

Research Data:
{json.dumps(combined_data, indent=2)}

Create a synthesized analysis that:
1. Integrates findings from all sources
2. Identifies consensus and conflicting information
3. Highlights key themes and patterns
4. Provides a cohesive narrative
5. Offers evidence-based conclusions
6. Suggests areas for further research

Ensure all claims are properly attributed to sources where possible.
"""

    def _build_general_research_prompt(self, query: str) -> str:
        """Build general research prompt for Claude."""
        return f"""
Conduct comprehensive research on the following topic: "{query}"

Please provide:
1. Overview and background information
2. Key findings and current state
3. Important trends and developments
4. Challenges and opportunities
5. Relevant data and statistics
6. Sources and references (when possible)

Focus on providing accurate, well-structured information with proper attribution where available.
"""

    def _extract_sources_from_perplexity(self, perplexity_data: Dict[str, Any]) -> List[str]:
        """Extract sources from Perplexity research data."""
        sources = []

        if "results" in perplexity_data:
            results = perplexity_data["results"]
            if "sources" in results:
                for source in results["sources"]:
                    if isinstance(source, dict):
                        if "url" in source:
                            sources.append(source["url"])
                        elif "title" in source:
                            sources.append(source["title"])
                    elif isinstance(source, str):
                        sources.append(source)

        return sources

    def _generate_fallback_sources(self, query: str) -> List[str]:
        """Generate fallback sources when MCP is unavailable."""
        return [
            f"Research conducted on: {query}",
            "Internal knowledge synthesis",
            "General industry analysis"
        ]

    def _generate_research_queries(self, topic: str) -> List[str]:
        """Generate multiple research queries for comprehensive coverage."""
        # Simple query generation - could be made more sophisticated
        queries = [
            f"{topic} overview and current state",
            f"{topic} challenges and opportunities",
            f"{topic} future trends and predictions"
        ]
        return queries

    async def _get_default_system_prompt(self) -> str:
        """Get default system prompt for research agent."""
        return """You are a specialized research agent focused on comprehensive research and knowledge synthesis. Your expertise includes:

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

## Current Task
Focus on conducting thorough research with proper source attribution and confidence scoring."""