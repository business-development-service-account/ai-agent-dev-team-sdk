"""
FrontEnd Coder - Specialized agent for frontend development.

Implements modern frontend development capabilities including
UI components, responsive design, and user experience optimization.
"""

import json
from typing import Dict, List, Optional, Any, Set
from datetime import datetime

from .base_agent import BaseAgent, TaskResult
from ..core.rules_engine import TaskSpec
from ..core.context_manager import AgentContext
from ..core.exceptions import TaskExecutionError


class FrontEndCoder(BaseAgent):
    """
    Specialized agent for frontend development with modern frameworks.
    Creates responsive, accessible user interfaces with best practices.
    """

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize FrontEndCoder."""
        super().__init__(agent_type="frontend", config=config)
        self.framework_preference = self.config.get("framework", "react")
        self.component_library = self.config.get("component_library", "material-ui")

    async def _initialize_capabilities(self):
        """Initialize frontend coder capabilities."""
        # UI Development capabilities
        self._add_capability(
            name="ui_development",
            description="Modern UI component development with React/Vue/Angular",
            supported_task_types={
                "component_development", "ui_implementation", "responsive_design"
            }
        )

        # Responsive Design capabilities
        self._add_capability(
            name="responsive_design",
            description="Mobile-first responsive design implementation",
            supported_task_types={
                "mobile_design", "responsive_layout", "cross_browser_compatibility"
            }
        )

        # Component Architecture capabilities
        self._add_capability(
            name="component_architecture",
            description="Reusable component architecture and design systems",
            supported_task_types={
                "component_system", "design_system", "component_library"
            }
        )

        # User Experience capabilities
        self._add_capability(
            name="user_experience",
            description="UX optimization and accessibility implementation",
            supported_task_types={
                "ux_optimization", "accessibility", "user_interface"
            }
        )

        # Task types specifically supported
        self.supported_task_types.update({
            "component_development", "ui_implementation", "responsive_design",
            "mobile_design", "responsive_layout", "cross_browser_compatibility",
            "component_system", "design_system", "component_library",
            "ux_optimization", "accessibility", "user_interface",
            "form_validation", "data_visualization", "state_management"
        })

    async def _execute_task_internal(
        self,
        task_spec: TaskSpec,
        context: Optional[AgentContext]
    ) -> TaskResult:
        """Execute frontend development task."""
        task_start_time = datetime.utcnow()

        try:
            # Extract frontend-specific parameters
            component_spec = task_spec.metadata.get("component_spec", {})
            design_requirements = task_spec.metadata.get("design_requirements", {})
            framework = task_spec.metadata.get("framework", self.framework_preference)

            # Determine task type and execute accordingly
            if task_spec.task_type in ["component_development", "component_system"]:
                result = await self._execute_component_development(
                    task_spec, component_spec, framework, context
                )
            elif task_spec.task_type in ["responsive_design", "mobile_design"]:
                result = await self._execute_responsive_design(
                    task_spec, design_requirements, context
                )
            elif task_spec.task_type in ["ux_optimization", "accessibility"]:
                result = await self._execute_ux_optimization(
                    task_spec, design_requirements, context
                )
            elif task_spec.task_type in ["form_validation", "data_visualization"]:
                result = await self._execute_feature_development(
                    task_spec, component_spec, context
                )
            else:
                result = await self._execute_general_frontend_task(
                    task_spec, context
                )

            # Add execution metadata
            result.metadata.update({
                "framework": framework,
                "component_complexity": task_spec.complexity,
                "development_duration": (datetime.utcnow() - task_start_time).total_seconds(),
                "frontend_version": "1.0.0"
            })

            return result

        except Exception as e:
            raise TaskExecutionError(f"Frontend development task failed: {e}") from e

    async def _execute_component_development(
        self,
        task_spec: TaskSpec,
        component_spec: Dict[str, Any],
        framework: str,
        context: Optional[AgentContext]
    ) -> TaskResult:
        """Execute component development task."""
        # Build component development prompt
        component_prompt = self._build_component_development_prompt(
            task_spec.task,
            component_spec,
            framework
        )

        messages = [{"role": "user", "content": component_prompt}]
        system_prompt = context.system_prompt if context else await self._get_default_system_prompt()

        claude_response = await self._call_claude(messages, system_prompt)

        # Generate component metadata
        component_metadata = {
            "component_name": component_spec.get("name", "Component"),
            "framework": framework,
            "props": component_spec.get("props", {}),
            "styling": component_spec.get("styling", "css"),
            "dependencies": self._generate_component_dependencies(framework)
        }

        return self._create_task_result(
            task_id=task_spec.task_id,
            content=claude_response,
            confidence_score=0.85,
            sources=[],
            metadata={
                "development_method": "claude_component",
                "component_metadata": component_metadata,
                "task_type": "component_development"
            }
        )

    async def _execute_responsive_design(
        self,
        task_spec: TaskSpec,
        design_requirements: Dict[str, Any],
        context: Optional[AgentContext]
    ) -> TaskResult:
        """Execute responsive design implementation."""
        # Build responsive design prompt
        responsive_prompt = self._build_responsive_design_prompt(
            task_spec.task,
            design_requirements
        )

        messages = [{"role": "user", "content": responsive_prompt}]
        system_prompt = context.system_prompt if context else await self._get_default_system_prompt()

        claude_response = await self._call_claude(messages, system_prompt)

        # Generate responsive design metadata
        responsive_metadata = {
            "breakpoints": ["320px", "768px", "1024px", "1200px"],
            "approach": "mobile_first",
            "technologies": ["flexbox", "grid", "media_queries"],
            "compatibility": ["modern_browsers", "ie11+"]
        }

        return self._create_task_result(
            task_id=task_spec.task_id,
            content=claude_response,
            confidence_score=0.83,
            sources=[],
            metadata={
                "development_method": "claude_responsive",
                "responsive_metadata": responsive_metadata,
                "task_type": "responsive_design"
            }
        )

    async def _execute_ux_optimization(
        self,
        task_spec: TaskSpec,
        design_requirements: Dict[str, Any],
        context: Optional[AgentContext]
    ) -> TaskResult:
        """Execute UX optimization and accessibility implementation."""
        # Build UX optimization prompt
        ux_prompt = self._build_ux_optimization_prompt(
            task_spec.task,
            design_requirements
        )

        messages = [{"role": "user", "content": ux_prompt}]
        system_prompt = context.system_prompt if context else await self._get_default_system_prompt()

        claude_response = await self._call_claude(messages, system_prompt)

        # Generate UX metadata
        ux_metadata = {
            "accessibility_standard": "WCAG 2.1 AA",
            "ux_principles": ["usability", "accessibility", "performance", "visual_hierarchy"],
            "optimization_areas": ["navigation", "forms", "content", "interactions"]
        }

        return self._create_task_result(
            task_id=task_spec.task_id,
            content=claude_response,
            confidence_score=0.82,
            sources=[],
            metadata={
                "development_method": "claude_ux",
                "ux_metadata": ux_metadata,
                "task_type": "ux_optimization"
            }
        )

    async def _execute_feature_development(
        self,
        task_spec: TaskSpec,
        component_spec: Dict[str, Any],
        context: Optional[AgentContext]
    ) -> TaskResult:
        """Execute specialized feature development."""
        # Build feature development prompt based on task type
        if task_spec.task_type == "form_validation":
            feature_prompt = self._build_form_validation_prompt(task_spec.task, component_spec)
        elif task_spec.task_type == "data_visualization":
            feature_prompt = self._build_data_visualization_prompt(task_spec.task, component_spec)
        else:
            feature_prompt = self._build_general_feature_prompt(task_spec.task, component_spec)

        messages = [{"role": "user", "content": feature_prompt}]
        system_prompt = context.system_prompt if context else await self._get_default_system_prompt()

        claude_response = await self._call_claude(messages, system_prompt)

        # Generate feature metadata
        feature_metadata = {
            "feature_type": task_spec.task_type,
            "complexity": task_spec.complexity,
            "interactions": component_spec.get("interactions", [])
        }

        return self._create_task_result(
            task_id=task_spec.task_id,
            content=claude_response,
            confidence_score=0.80,
            sources=[],
            metadata={
                "development_method": "claude_feature",
                "feature_metadata": feature_metadata,
                "task_type": task_spec.task_type
            }
        )

    async def _execute_general_frontend_task(
        self,
        task_spec: TaskSpec,
        context: Optional[AgentContext]
    ) -> TaskResult:
        """Execute general frontend development task."""
        # Build general frontend prompt
        general_prompt = self._build_general_frontend_prompt(task_spec.task)

        messages = [{"role": "user", "content": general_prompt}]
        system_prompt = context.system_prompt if context else await self._get_default_system_prompt()

        claude_response = await self._call_claude(messages, system_prompt)

        return self._create_task_result(
            task_id=task_spec.task_id,
            content=claude_response,
            confidence_score=0.78,
            sources=[],
            metadata={
                "development_method": "claude_general",
                "task_type": "general_frontend"
            }
        )

    def _build_component_development_prompt(
        self,
        task_description: str,
        component_spec: Dict[str, Any],
        framework: str
    ) -> str:
        """Build component development prompt."""
        component_info = json.dumps(component_spec, indent=2)

        return f"""
Create a modern, production-ready {framework} component based on the following requirements:

Task Description: {task_description}

Component Specification:
{component_info}

Please provide:
1. Complete component code with proper structure
2. PropTypes/TypeScript interfaces (if applicable)
3. Styling implementation (CSS modules, styled-components, or inline styles)
4. Component documentation with usage examples
5. Accessibility considerations (ARIA labels, keyboard navigation)
6. State management (if applicable)
7. Error handling and edge cases
8. Unit test examples
9. Responsive design considerations

Requirements:
- Follow modern {framework} best practices
- Ensure accessibility compliance (WCAG 2.1 AA)
- Include proper error handling
- Make component reusable and maintainable
- Add comprehensive comments
- Consider performance optimizations
"""

    def _build_responsive_design_prompt(
        self,
        task_description: str,
        design_requirements: Dict[str, Any]
    ) -> str:
        """Build responsive design prompt."""
        design_info = json.dumps(design_requirements, indent=2)

        return f"""
Implement a responsive design solution for the following requirements:

Task Description: {task_description}

Design Requirements:
{design_info}

Please provide:
1. Mobile-first responsive CSS/SCSS implementation
2. Breakpoint strategy and media queries
3. Flexible layout using CSS Grid and Flexbox
4. Responsive typography and spacing
5. Image and media optimization
6. Cross-browser compatibility considerations
7. Touch-friendly interaction design
8. Performance optimization techniques
9. Progressive enhancement approach

Requirements:
- Support common screen sizes (mobile, tablet, desktop)
- Use semantic HTML5 elements
- Implement proper accessibility features
- Optimize for performance and loading speed
- Ensure touch interaction compatibility
"""

    def _build_ux_optimization_prompt(
        self,
        task_description: str,
        design_requirements: Dict[str, Any]
    ) -> str:
        """Build UX optimization prompt."""
        design_info = json.dumps(design_requirements, indent=2)

        return f"""
Optimize the user experience for the following requirements:

Task Description: {task_description}

Design Requirements:
{design_info}

Please provide:
1. User interface improvements based on UX principles
2. Accessibility implementations (WCAG 2.1 AA compliance)
3. Navigation and information architecture improvements
4. Form usability enhancements
5. Error handling and user feedback improvements
6. Loading states and micro-interactions
7. Performance optimizations for better UX
8. Cognitive load reduction techniques
9. A/B testing recommendations

Requirements:
- Follow established UX heuristics and principles
- Ensure full accessibility compliance
- Improve usability for all user groups
- Provide clear user feedback and guidance
- Optimize for user engagement and conversion
"""

    def _build_form_validation_prompt(
        self,
        task_description: str,
        form_spec: Dict[str, Any]
    ) -> str:
        """Build form validation prompt."""
        form_info = json.dumps(form_spec, indent=2)

        return f"""
Create a comprehensive form validation system for the following requirements:

Task Description: {task_description}

Form Specification:
{form_info}

Please provide:
1. Form component with validation logic
2. Real-time validation feedback
3. Custom validation rules and messages
4. Error state handling and display
5. Success state and submission handling
6. Accessibility features for form inputs
7. Mobile-optimized form layouts
8. Progressive form enhancement
9. Security considerations (CSRF, XSS protection)

Requirements:
- Validate on input and submission
- Provide clear, helpful error messages
- Support keyboard navigation
- Ensure accessibility compliance
- Handle edge cases gracefully
- Optimize for mobile devices
"""

    def _build_data_visualization_prompt(
        self,
        task_description: str,
        viz_spec: Dict[str, Any]
    ) -> str:
        """Build data visualization prompt."""
        viz_info = json.dumps(viz_spec, indent=2)

        return f"""
Create an interactive data visualization component for the following requirements:

Task Description: {task_description}

Visualization Specification:
{viz_info}

Please provide:
1. Interactive chart/graph component
2. Data processing and transformation logic
3. Responsive design for mobile and desktop
4. Accessibility features for data visualization
5. Loading states and error handling
6. Interactive features (zoom, filter, export)
7. Color scheme and styling for clarity
8. Performance optimization for large datasets
9. Cross-browser compatibility

Requirements:
- Use modern charting libraries (Chart.js, D3.js, etc.)
- Ensure accessibility compliance
- Optimize for performance with large datasets
- Provide intuitive user interactions
- Support responsive design
- Include comprehensive error handling
"""

    def _build_general_feature_prompt(
        self,
        task_description: str,
        feature_spec: Dict[str, Any]
    ) -> str:
        """Build general feature development prompt."""
        feature_info = json.dumps(feature_spec, indent=2)

        return f"""
Implement the frontend feature with the following requirements:

Task Description: {task_description}

Feature Specification:
{feature_info}

Please provide:
1. Complete feature implementation
2. Component structure and organization
3. State management approach
4. User interface and interaction design
5. Error handling and edge cases
6. Performance considerations
7. Accessibility features
8. Testing strategy and examples
9. Documentation and usage examples

Requirements:
- Follow modern frontend best practices
- Ensure accessibility compliance
- Implement proper error handling
- Optimize for performance
- Provide clear documentation
- Consider maintainability and scalability
"""

    def _build_general_frontend_prompt(self, task_description: str) -> str:
        """Build general frontend development prompt."""
        return f"""
Implement the frontend solution for the following requirement:

Task Description: {task_description}

Please provide:
1. Complete frontend implementation
2. Modern framework usage (React, Vue, or Angular)
3. Responsive design implementation
4. Component-based architecture
5. State management approach
6. Styling and design system
7. Accessibility features
8. Performance optimizations
9. Testing considerations
10. Documentation and usage examples

Requirements:
- Use modern frontend frameworks and tools
- Ensure mobile-responsive design
- Follow accessibility best practices
- Implement proper error handling
- Optimize for performance and user experience
- Provide clear, maintainable code
"""

    def _generate_component_dependencies(self, framework: str) -> List[str]:
        """Generate component dependencies based on framework."""
        dependencies = {
            "react": ["react", "prop-types"],
            "vue": ["vue", "vue-router"],
            "angular": ["@angular/core", "@angular/common"],
            "svelte": ["svelte"]
        }

        base_deps = dependencies.get(framework, [])
        styling_deps = ["styled-components"] if self.component_library == "styled-components" else []

        return base_deps + styling_deps

    async def _get_default_system_prompt(self) -> str:
        """Get default system prompt for frontend coder."""
        return """You are a specialized frontend developer focused on creating modern, responsive user interfaces. Your expertise includes:

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
Focus on creating high-quality, production-ready frontend components with modern best practices."""